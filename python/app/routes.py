from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import json
from pymongo import MongoClient

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("Content-Type") == "application/x-www-form-urlencoded":
        data = json.loads(request.form.get("payload", "{}"))
    else:
        data = request.json

    # Extract the source URL
    sender = data.get("sender", {}) or {}
    source_url = sender.get("url", "")
    
    # Determine source
    if "github.com" in source_url:
        source = "github"
        # Handle GitHub webhook events
        event_type = request.headers.get("X-GitHub-Event")
        if event_type in ["push", "pull_request"]:
            db = get_db()
            
            # Extract common fields
            sha = data.get("after") or data.get("pull_request", {}).get("head", {}).get("sha")
            ref = data.get("ref")  # For push events
            branch = ref.split("/")[-1] if ref else data.get("pull_request", {}).get("head", {}).get("ref")
            
            # Record git event
            event = {
                'timestamp': datetime.utcnow(),
                'type': 'push' if event_type == 'push' else 'merge',
                'sha': sha,
                'author': sender.get("login"),
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
            
    elif "linear.app" in source_url:
        source = "linear"
    elif "atlassian.net" in source_url:
        source = "jira"
    else:
        source = "unknown"
    
    return jsonify({"message": f"Webhook received from {source}"}), 200
