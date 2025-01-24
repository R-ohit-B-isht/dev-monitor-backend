from flask import Blueprint, request, jsonify, current_app
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from .utils.anonymization import hash_engineer_id, obfuscate_repository_name
from typing import Optional
import re

tasks_bp = Blueprint("tasks", __name__)

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    db = client[current_app.config["MONGODB_DB"]]
    
    # Update tasks collection validator if it exists
    if 'tasks' in db.list_collection_names():
        db.command({
            'collMod': 'tasks',
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['title', 'status', 'integration'],
                    'properties': {
                        'status': {
                            'enum': ['To-Do', 'In-Progress', 'Done', 'Deleted'],
                            'description': 'must be one of the enum values and is required'
                        }
                    }
                }
            }
        })
    return db

@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    db = get_db()
    filters = {}

    # Add filter support for status, integration, priority, search, and meeting tasks
    status = request.args.get("status")
    integration = request.args.get("integration")
    priority = request.args.get("priority")
    search = request.args.get("search")
    # Removed meeting-related filtering for AI agent

    # Always exclude deleted tasks unless explicitly requested
    show_deleted = request.args.get("showDeleted") == "true"
    if not show_deleted:
        filters["$and"] = filters.get("$and", [])
        filters["$and"].append({
            "$or": [
                {"$and": [
                    {"status": {"$ne": "Deleted"}},
                    {"isDeleted": {"$ne": True}}
                ]},
                {"$and": [
                    {"status": {"$ne": "Deleted"}},
                    {"isDeleted": {"$exists": False}}
                ]}
            ]
        })

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

    # Removed meeting filter for AI agent

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
        # Check if we should show deleted tasks
        show_deleted = request.args.get("showDeleted") == "true"

        # Build query
        query = {"_id": ObjectId(task_id)}
        if not show_deleted:
            query["status"] = {"$ne": "Deleted"}

        task = db.tasks.find_one(query)
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

    # Add required timestamps and soft delete flag
    data["createdAt"] = datetime.utcnow()
    data["updatedAt"] = datetime.utcnow()
    data["isDeleted"] = False  # Initialize as not deleted

    # Validate required fields
    required_fields = ["title", "status", "integration"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Removed meeting-specific fields for AI agent

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

@tasks_bp.route("/tasks/create", methods=["POST"])
def create_task_alias():
    """Alias route for task creation to maintain compatibility"""
    return create_task()

def create_task_internal_call(
    title: str,
    status: str,
    integration: str,
    description: Optional[str] = None,
    is_deleted: bool = False,
    engineer_id: Optional[str] = None,
    repository: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    duration: Optional[int] = None,
    is_recurring: bool = False,
    recurrence_pattern: Optional[str] = None,
    recurrence_days: Optional[list] = None,
    participants: Optional[list] = None,
    platform: Optional[str] = None,
    branch: Optional[str] = None,
    **additional_data
):
    db = get_db()
    # Initialize data dictionary with required fields
    data = {
        "title": title,
        "status": status,
        "integration": integration,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
        "isDeleted": is_deleted
    }

    # Add optional description
    if description:
        data["description"] = description

    # Add all additional data
    data.update(additional_data)

    # Removed meeting detection for AI agent

    # Handle sensitive data
    if engineer_id:
        data["engineerId"] = hash_engineer_id(engineer_id)

    if repository:
        data["repository"] = obfuscate_repository_name(repository)

    # Generate branch name if not provided
    if not branch:
        # Convert title to kebab case and clean special characters
        branch_name = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        branch_name = re.sub(r'\s+', '-', branch_name)
        data["branch"] = f"task/{branch_name}"
    else:
        data["branch"] = branch

    # Insert into database
    result = db.tasks.insert_one(data)

    return {
        "_id": str(result.inserted_id),
        "branch": data["branch"]
    }, 201

@tasks_bp.route("/tasks/<task_id>", methods=["PATCH"])
def update_task(task_id):
    db = get_db()
    updates = request.json
    print(f"Received PATCH request for task {task_id}")
    print(f"Request data: {updates}")

    try:
        # Get current task state
        current_task = db.tasks.find_one({"_id": ObjectId(task_id)})
        if not current_task:
            print(f"Task {task_id} not found")
            return jsonify({"error": "Task not found"}), 404

        # Handle soft delete
        if updates.get("delete") == True:
            print(f"Processing soft delete for task {task_id}")
            current_time = datetime.utcnow()
            delete_updates = {
                "status": "Deleted",
                "updatedAt": current_time
            }
            print(f"Soft delete updates: {delete_updates}")

            result = db.tasks.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": delete_updates}
            )

            if result.modified_count == 0:
                return jsonify({"error": "Task not found or already deleted"}), 404

            try:
                response_data = {
                    "message": "Task deleted successfully",
                    "taskId": str(task_id),
                    "updatedAt": current_time.isoformat()
                }
                return jsonify(response_data), 200
            except Exception as e:
                print(f"Error serializing delete response: {str(e)}")
                return jsonify({"error": "Failed to process delete response"}), 400

        # For non-delete updates
        current_time = datetime.utcnow()
        if "updatedAt" not in updates:
            updates["updatedAt"] = current_time

        # Ensure status is valid if it's being updated
        if "status" in updates and updates["status"] not in ["To-Do", "In-Progress", "Done", "Deleted"]:
            return jsonify({"error": f"Invalid status: {updates['status']}"}), 400

        # Update task
        result = db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": updates}
        )

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
                value_stream_event = {
                    "engineerId": hash_engineer_id(updates.get("engineerId", current_task.get("engineerId"))),
                    "taskId": ObjectId(task_id),
                    "eventType": event_type,
                    "timestamp": datetime.utcnow(),
                    "metadata": {
                        "previousStatus": current_task.get("status"),
                        "newStatus": updates["status"]
                    },
                    "sessionId": updates.get("sessionId")
                }
                db.value_stream_events.insert_one(value_stream_event)

        try:
            # Format datetime for JSON serialization
            updated_at = updates["updatedAt"]
            if isinstance(updated_at, datetime):
                updated_at = updated_at.isoformat()
            
            response_data = {
                "message": "Task updated",
                "taskId": str(task_id),
                "updatedAt": updated_at
            }
            return jsonify(response_data), 200
        except Exception as e:
            print(f"Error serializing update response: {str(e)}")
            return jsonify({"error": "Failed to process update response"}), 400
    except Exception as e:
        print(f"Error in update_task: {str(e)}")
        return jsonify({"error": str(e)}), 400
