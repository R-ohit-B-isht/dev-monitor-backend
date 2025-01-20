from flask import Blueprint, request, jsonify
import json

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
    elif "linear.app" in source_url:
        source = "linear"
    elif "atlassian.net" in source_url:
        source = "jira"
    else:
        source = "unknown"
    
    return jsonify({"message": f"Webhook received from {source}"}), 200
