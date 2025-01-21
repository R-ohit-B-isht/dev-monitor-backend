from flask import Blueprint, request, jsonify, current_app
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timezone
from .utils.anonymization import hash_engineer_id, obfuscate_repository_name
import re

tasks_bp = Blueprint("tasks", __name__)

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    db = get_db()
    filters = {}
    
    # Add filter support for status, integration, priority, search, and meeting tasks
    status = request.args.get("status")
    integration = request.args.get("integration")
    priority = request.args.get("priority")
    search = request.args.get("search")
    exclude_meetings = request.args.get("excludeMeetings") == "true"
    
    if status:
        filters["status"] = status
    if integration:
        filters["integration"] = integration
    if priority:
        filters["priority"] = priority
    
    # Build search query
    search_conditions = []
    if search:
        search_conditions.extend([
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ])
    
    # Add meeting filter
    if exclude_meetings:
        meeting_keywords = ["meeting", "zoom", "call", "sync", "standup", "review"]
        meeting_pattern = "|".join(meeting_keywords)
        filters["$and"] = filters.get("$and", [])
        filters["$and"].append({
            "$nor": [
                {"title": {"$regex": meeting_pattern, "$options": "i"}},
                {"description": {"$regex": meeting_pattern, "$options": "i"}}
            ]
        })
    
    # Combine search conditions if they exist
    if search_conditions:
        filters["$or"] = search_conditions
        
    tasks = list(db.tasks.find(filters))
    
    # Convert ObjectId to string for JSON serialization
    for task in tasks:
        task["_id"] = str(task["_id"])
        
    return jsonify(tasks), 200

@tasks_bp.route("/tasks/<task_id>", methods=["GET"])
def get_task(task_id):
    db = get_db()
    try:
        task = db.tasks.find_one({"_id": ObjectId(task_id)})
        if task:
            task["_id"] = str(task["_id"])
            return jsonify(task), 200
        return jsonify({"error": "Task not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    db = get_db()
    data = request.json
    
    # Add required timestamps
    data["createdAt"] = datetime.now(timezone.utc)
    data["updatedAt"] = datetime.now(timezone.utc)
    
    # Validate required fields
    required_fields = ["title", "status", "integration"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
        
    # Handle meeting-specific fields
    if any(keyword in data.get("title", "").lower() or keyword in data.get("description", "").lower() 
           for keyword in ["meeting", "zoom", "call", "sync", "standup", "review"]):
        # Add meeting metadata
        data["isMeeting"] = True
        data["meetingMetadata"] = {
            "startTime": data.get("startTime"),
            "endTime": data.get("endTime"),
            "duration": data.get("duration", 0),
            "isRecurring": data.get("isRecurring", False),
            "recurrencePattern": data.get("recurrencePattern", None),  # daily, weekly, monthly
            "recurrenceDays": data.get("recurrenceDays", []),  # [0-6] for weekdays
            "participants": data.get("participants", []),
            "platform": data.get("platform", "unknown")  # zoom, teams, meet, etc.
        }
    
    # Anonymize sensitive data
    if "engineerId" in data:
        data["engineerId"] = hash_engineer_id(data["engineerId"])
    if "repository" in data:
        data["repository"] = obfuscate_repository_name(data["repository"])
    
    # Generate branch name from title
    if "branch" not in data:
        # Convert title to kebab case and clean special characters
        branch = re.sub(r'[^a-zA-Z0-9\s-]', '', data["title"].lower())
        branch = re.sub(r'\s+', '-', branch)
        data["branch"] = f"task/{branch}"
        
    result = db.tasks.insert_one(data)
    return jsonify({
        "_id": str(result.inserted_id),
        "branch": data["branch"]
    }), 201

@tasks_bp.route("/tasks/<task_id>", methods=["PATCH"])
def update_task(task_id):
    db = get_db()
    updates = request.json
    
    # Get current task state
    current_task = db.tasks.find_one({"_id": ObjectId(task_id)})
    if not current_task:
        return jsonify({"error": "Task not found"}), 404
        
    # Add updated timestamp
    updates["updatedAt"] = datetime.now(timezone.utc)
    
    # If updating status to Done, check if this task is blocked by any tasks
    if updates.get("status") == "Done":
        print(f"Checking if task {task_id} can be marked as Done")
        print(f"Current task status: {current_task.get('status')}")
        
        # Check if this task is being blocked by others (where this task is the target)
        blocking_relationships = list(db.relationships.find({
            "targetTaskId": str(task_id),  # This task is being blocked
            "type": "blocks"  # Only check for direct blocking relationships
        }))
        print(f"Found {len(blocking_relationships)} blocking relationships")
        
        # Only check blocking tasks if this task is being blocked
        for rel in blocking_relationships:
            print(f"Checking relationship: {rel}")
            blocking_task = db.tasks.find_one({"_id": ObjectId(rel["sourceTaskId"])})
            print(f"Found blocking task: {blocking_task}")
            
            if blocking_task and blocking_task["status"] != "Done":
                print(f"Blocking task {blocking_task['title']} is not Done")
                return jsonify({
                    "error": f"Cannot mark as Done: blocked by task '{blocking_task['title']}' which is not Done"
                }), 400
        print("No blocking tasks found or all blocking tasks are Done, allowing update")
    
    # Update task
    result = db.tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": updates}
    )
    
    if result.modified_count == 0:
        return jsonify({"error": "Task not found or no changes made"}), 404
    
    # Record value stream event if status changed
    if "status" in updates and updates["status"] != current_task.get("status"):
        event_type = None
        if updates["status"] == "In-Progress":
            event_type = "code_started"
        elif updates["status"] == "Review":
            event_type = "review_started"
        elif updates["status"] == "Done":
            event_type = "code_completed"
            
        if event_type:
            # Get engineerId from updates or current task
            engineer_id = updates.get("engineerId") or current_task.get("engineerId")
            
            # Only create value stream event if we have an engineerId
            if engineer_id:
                value_stream_event = {
                    "engineerId": hash_engineer_id(engineer_id),
                    "taskId": ObjectId(task_id),
                    "eventType": event_type,
                    "timestamp": datetime.now(timezone.utc),
                    "metadata": {
                        "previousStatus": current_task.get("status"),
                        "newStatus": updates["status"]
                    },
                    "sessionId": updates.get("sessionId")
                }
                db.value_stream_events.insert_one(value_stream_event)
    
    return jsonify({
        "message": "Task updated",
        "taskId": str(task_id),
        "updatedAt": updates["updatedAt"].isoformat()
    }), 200
