from app.devin_service import trigger_devin_session
from flask import Blueprint, current_app, request, jsonify
from typing import Dict, Optional
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
from pymongo import MongoClient

linear_bp = Blueprint("linear", __name__)

class LinearAPI:
    def __init__(self, api_token: str):
        
        self.api_token = api_token
        self.endpoint = "https://api.linear.app/graphql"
        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }
        
        # Set up GQL client
        transport = RequestsHTTPTransport(
            url=self.endpoint,
            headers=self.headers
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def execute_query(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict]:
        
        try:
            return self.client.execute(gql(query), variable_values=variables)
        except Exception as e:
            print(f"Error executing query: {e}")
            return None

    def get_issue(self, issue_id: str) -> Optional[Dict]:
        
        query = """
        query Issue($id: String!) {
          issue(id: $id) {
            id
            title
            description
            state {
              name
            }
            assignee {
              name
              email
            }
            priority
            labels {
              nodes {
                name
              }
            }
          }
        }
        """
        variables = {"id": issue_id}
        result = self.execute_query(query, variables)
        return result["issue"] if result else None

    def add_comment(self, issue_id: str, body: str) -> Optional[Dict]:
        mutation = """
        mutation CreateComment($issueId: String!, $body: String!) {
          commentCreate(input: {
            issueId: $issueId
            body: $body
          }) {
            success
            comment {
              id
              body
            }
          }
        }
        """
        variables = {
            "issueId": issue_id,
            "body": body
        }
        result = self.execute_query(mutation, variables)
        return result["commentCreate"]["comment"] if result and result["commentCreate"]["success"] else None

@linear_bp.route("/webhooks/linear", methods=["POST"])
def linear_webhook():
    """Handle Linear webhook events"""
    try:
        return handle_linear_webhook(request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handle_linear_webhook(data: Dict) -> Dict:
    """Process Linear webhook data and trigger Devin session if needed"""
    issue_id = data.get("data", {}).get("issueId", "")
    comment_body = data.get("data", {}).get("body", "")
    action = data.get("action","")
    filters = current_app.config["FILTERS"]["linear"]

    if filters["trigger_mention"] in comment_body and action == "create" :
        
        api_token = current_app.config["LINEAR"]["api_token"]

        # Initialize Linear API client
        linear_client = LinearAPI(api_token)
        
        # Retrieve the issue details
        issue_details = linear_client.get_issue(issue_id)
        if not issue_details:
            print(f"Failed to fetch issue details for {issue_id}")
            return {"error": "Failed to fetch issue details"}

        # Extract issue details safely
        title = issue_details.get("title", "")
        description = issue_details.get("description", "")

        # Format prompt with available data
        prompt = filters["prompt_template"].format(
            comment=comment_body,
            issue_title=title,
            issue_description=description
        )

        # Trigger Devin session
        devin_response = trigger_devin_session(prompt)
        if not devin_response or "error" in devin_response:
            print("Failed to create Devin session")
            return {"error": "Failed to create Devin session"}

        # Post comment with session URL
        comment = "Devin Session Link : " + devin_response.get("url", "🥲 Sorry No URL generated")
        if not linear_client.add_comment(issue_id, comment):
            print("Failed to post comment to Linear")
            # Continue anyway since we have the Devin session
        
        # Create task in MongoDB
        client = MongoClient(current_app.config["MONGODB_URI"])
        db = client[current_app.config["MONGODB_DB"]]
        
        # Handle case where issue_details might be None
        title = ""
        description = ""
        priority = None
        
        if issue_details:
            title = issue_details.get("title", "")
            description = issue_details.get("description", "")
            priority = issue_details.get("priority")
        
        new_task = {
            "title": title,
            "description": description,
            "status": "To-Do",
            "integration": "linear",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "devinSessionUrl": devin_response.get("url"),
            "sourceId": issue_id,
            "priority": priority
        }
        
        db.tasks.insert_one(new_task)
        client.close()
        
        return devin_response
    
    return {"message": "No action triggered for Linear."}
