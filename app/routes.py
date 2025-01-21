from flask import Blueprint, request, jsonify
from app import github_service, jira_service, linear_service
import json

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    print(request.headers.get("Content-Type"))


    # Identify the source of the webhook
    # Check Content-Type
    if request.headers.get("Content-Type") == "application/x-www-form-urlencoded":
        data = json.loads(request.form.get("payload", "{}"))  # Parse payload field
    else:
        data = request.json  # Incoming webhook payload

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


    # print(data)
    # print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    # print(source_url)

    # Check if it's from GitHub (you can adjust the exact check if needed)
    if "github.com" in source_url:
        source = "github"
    elif "linear.app" in source_url:
        source = "linear"
    elif "atlassian.net" in source_url:
        source = "jira"
    else:
        source = "unknown"  # Or whatever fallback you want for unsupported sources

    # Debug: Log the extracted source
    print(f"Source: {source}")


    if "jira" in source:
        response = jira_service.handle_jira_webhook(data)
    elif "linear" in source:
        response = linear_service.handle_linear_webhook(data)
    elif "github" in source:
        response = github_service.handle_github_webhook(data)
    else:
        response = {"message": "Unsupported source"}

    return jsonify(response), 200
