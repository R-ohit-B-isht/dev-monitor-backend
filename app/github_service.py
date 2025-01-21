from flask import current_app
from pymongo import MongoClient
from datetime import datetime
from .devin_service import trigger_devin_session

def handle_github_webhook(data):
    """Handle GitHub webhook events"""
    try:
        event_type = data.get("action")
        if not event_type:
            return {"message": "No action in webhook data"}

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
        if not task and event.get("message"):
            # Look for task ID in commit message or PR title
            import re
            task_id_match = re.search(r'#(\d+)', event.get("message", ""))
            if task_id_match:
                task = db.tasks.find_one({"taskId": task_id_match.group(1)})
        
        if task:
            event['taskId'] = task['_id']
        
        db.git_events.insert_one(event)
        client.close()
        
        # Check for @devin mentions in PR comments
        if event_type == "created" and data.get("comment"):
            comment_body = data.get("comment", {}).get("body", "")
            filters = current_app.config["FILTERS"]["github"]
            
            if filters["trigger_mention"] in comment_body:
                issue_url = data.get("issue", {}).get("html_url") or data.get("pull_request", {}).get("html_url")
                issue = data.get("issue") or data.get("pull_request", {})
                
                prompt = filters["prompt_template"].format(
                    url=issue_url,
                    comment=comment_body,
                    issue=issue.get("title", "") + "\n" + issue.get("body", "")
                )
                
                devin_response = trigger_devin_session(prompt)
                return devin_response
        
        return {"message": "Event recorded successfully", "event": event}
        
    except Exception as e:
        return {"error": f"Failed to handle GitHub webhook: {str(e)}"}
