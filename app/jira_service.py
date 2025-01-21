from app.devin_service import trigger_devin_session
from flask import Blueprint, current_app, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, Optional
from datetime import datetime
from pymongo import MongoClient

jira_bp = Blueprint("jira", __name__)


class JiraAPI:
    def __init__(self, domain: str, email: str, api_token: str):
        
        self.base_url = f"https://{domain}"
        self.auth = HTTPBasicAuth(email, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_issue(self, issue_key: str) -> Optional[Dict]:
        
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"
        try:
            response = requests.get(
                url,
                headers=self.headers,
                auth=self.auth
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving issue: {e}")
            return None
    
    def post_comment(self,issue_key: str, comment:str) -> bool:
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment"
        payload = {
            "body": comment
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                auth=self.auth
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error posting comment: {e}")
            return False


@jira_bp.route("/webhooks/jira", methods=["POST"])
def jira_webhook():
    """Handle Jira webhook events"""
    try:
        return handle_jira_webhook(request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handle_jira_webhook(data: Dict) -> Dict:
    """Process Jira webhook data and trigger Devin session if needed"""
    # Extract issue details from the webhook data
    issue = data.get("issue", {})
    comment = data.get("comment", {})
    comment_body = comment.get("body", "")
    action = data.get("webhookEvent","")

    # Get filters from Flask app config
    filters = current_app.config["FILTERS"]["jira"]

    # Check if the trigger mention is in the comment
    if filters["trigger_mention"] in comment_body and action == "comment_created":
        # Extract issue key from webhook data
        issue_key = issue.get("key", "")
        domain = current_app.config["JIRA"]["domain"]
        email = current_app.config["JIRA"]["email"]
        api_token = current_app.config["JIRA"]["api_token"]

        # Initialize Jira API client
        jira_client = JiraAPI(domain, email, api_token)
        
        # Retrieve the issue details
        issue_details = jira_client.get_issue(issue_key)

        if issue_details:
            issue_url = issue_details.get("self", "")
            issue_summary = issue_details.get("fields",{}).get("summary","")
            issue_description = issue_details.get("fields",{}).get("description","")

            # Format the prompt with the issue URL
            prompt = filters["prompt_template"].format(comment=comment_body, issue_summary=issue_summary, issue_description=issue_description)
            
            devin_response = trigger_devin_session(prompt)
            comment = "Devin Session Link : " + devin_response.get("url","🥲 Sorry No URL generated")
            if not jira_client.post_comment(issue_key, comment):
                print("Failed to post comment to Jira")
            
            # Create task in MongoDB
            client = MongoClient(current_app.config["MONGODB_URI"])
            db = client[current_app.config["MONGODB_DB"]]
            
            new_task = {
                "title": issue_summary,
                "description": issue_description,
                "status": "To-Do",
                "integration": "jira",
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
                "devinSessionUrl": devin_response.get("url"),
                "sourceUrl": issue_url,
                "issueKey": issue_key
            }
            
            db.tasks.insert_one(new_task)
            client.close()
            
            return devin_response

    return {"message": "No action triggered for Jira."}
