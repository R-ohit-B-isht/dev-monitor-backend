from flask import Blueprint, request, jsonify
from app import jira_service, linear_service, github_service
import json

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("Content-Type") == "application/x-www-form-urlencoded":
        data = json.loads(request.form.get("payload", "{}"))
    else:
        data = request.json

    # Extract the source URL
    sender=""
    source_url=""
    if data.get("sender", ""):
        sender=data.get("sender", "")
        source_url = sender.get("url", "")
    elif data.get("issue", {}).get("self",""):
        sender=data.get("issue", {})
        source_url = sender.get("self","")
    elif data.get("actor",{}).get("avatarUrl",""):
        sender=data.get("actor",{})
        source_url = sender.get("avatarUrl","")

    # Determine source
    if "github.com" in source_url:
        source = "github"
        response = github_service.handle_github_webhook(data)

    elif "linear.app" in source_url:
        source = "linear"
        response = linear_service.handle_linear_webhook(data)
    elif "atlassian.net" in source_url:
        source = "jira"
        response = jira_service.handle_jira_webhook(data)
    else:
        source = "unknown"
        response = {"message": "Unsupported source"}

    return jsonify(response), 200
