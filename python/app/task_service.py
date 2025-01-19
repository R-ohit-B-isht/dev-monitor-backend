from flask import Blueprint, request, jsonify, current_app
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

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
    data["createdAt"] = datetime.utcnow()
    data["updatedAt"] = datetime.utcnow()
    
    # Validate required fields
    required_fields = ["title", "status", "integration"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
        
    result = db.tasks.insert_one(data)
    return jsonify({"_id": str(result.inserted_id)}), 201

@tasks_bp.route("/tasks/<task_id>", methods=["PATCH"])
def update_task(task_id):
    db = get_db()
    updates = request.json
    
    # Add updated timestamp
    updates["updatedAt"] = datetime.utcnow()
    
    try:
        result = db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": updates}
        )
        if result.modified_count == 0:
            return jsonify({"error": "Task not found"}), 404
        return jsonify({"message": "Task updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
