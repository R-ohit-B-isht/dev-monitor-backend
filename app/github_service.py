from flask import current_app
from pymongo import MongoClient
from datetime import datetime
from .devin_service import trigger_devin_session
from typing import Optional, Dict, Any
from typing import Union
import requests
from requests.auth import HTTPBasicAuth
from .task_service import create_task_internal_call

class GitHubAPI:
    def __init__(self, api_token: str):

        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {api_token}",
        }

    def add_comment(self, issue_url: str, body: str) -> Optional[Dict]:

        url = f"{issue_url}/comments"

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json={"body": body}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error adding comment: {e}")
            return None

def serialize_mongodb_obj(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB object to JSON serializable format."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, ObjectId):
                obj[key] = str(value)
            elif isinstance(value, datetime):
                obj[key] = value.isoformat()
            elif isinstance(value, dict):
                obj[key] = serialize_mongodb_obj(value)
    return obj

def handle_github_webhook(data):
    """Handle GitHub webhook events"""
    try:
        event_type = data.get("action")
        if not event_type:
            return {"message": "No action in webhook data"}
        if not event_type == "created":
            return {"message": "Unexpected event type"}
        # Extract common fields
        sha = data.get("after") or data.get("pull_request", {}).get("head", {}).get("sha")
        ref = data.get("ref")  # For push events
        branch = ref.split("/")[-1] if ref else data.get("pull_request", {}).get("head", {}).get("ref")

        # Record git event
        client = MongoClient(current_app.config["MONGODB_URI"])
        db = client[current_app.config["MONGODB_DB"]]

        event = {
            'timestamp': datetime.utcnow(),
            'type': 'push' if event_type == 'push' else 'merge',
            'sha': sha,
            'author': data.get("sender", {}).get("login"),
            'message': data.get("head_commit", {}).get("message") if event_type == "push" else data.get("pull_request", {}).get("title"),
            'branch': branch,
            'metadata': {
                'event_type': event_type,
                'repository': data.get("repository", {}).get("full_name")
            }
        }

        # Try to link with task using branch name or PR title
        task = None
        if branch:
            task = db.tasks.find_one({"branch": branch})
        if task:
            event['taskId'] = task['_id']

        db.git_events.insert_one(event)
        client.close()

        # Check for @devin mentions in PR comments
        if event_type == "created" and data.get("comment"):
            comment_body = data.get("comment", {}).get("body", "")
            action = data.get("action","")
            filters = current_app.config["FILTERS"]["github"]

            if filters["trigger_mention"] in comment_body:
                issue_url = data.get("issue", {}).get("url", "")
                issue = data.get("issue") or data.get("pull_request", {})
                api_token = current_app.config["GITHUB"]["api_token"]
                github_client = GitHubAPI(api_token)

                prompt = filters["prompt_template"].format(
                    url=issue_url,
                    comment=comment_body,
                    issue=issue.get("title", "") + "\n" + issue.get("body", "")
                )

                devin_response = trigger_devin_session(prompt)
                comment = "Devin Session Link : " + devin_response.get("url","🥲 Sorry No URL generated")
                comment_response = github_client.add_comment(issue_url, comment)

                if not task:
                    create_task_internal_call(
                        title=issue.get("title", ""),
                        status="In-Progress",
                        integration="github",
                        description=issue.get("body",""),
                        repository=data.get("repository", {}).get("full_name"),
                        platform="github",
                        branch=branch
                    )
                return devin_response

        return {"message": "Event recorded successfully", "event": serialize_mongodb_obj(event)}

    except Exception as e:
        return {"error": f"Failed to handle GitHub webhook: {str(e)}"}
