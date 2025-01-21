from flask import Blueprint, request, jsonify, current_app
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import json

relationships_bp = Blueprint("relationships", __name__)

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

@relationships_bp.route("/relationships", methods=["GET"])
def get_relationships():
    """Get relationships with optional filtering"""
    db = get_db()
    filters = {}
    
    # Add filter support for source and target tasks
    source_task_id = request.args.get("sourceTaskId")
    target_task_id = request.args.get("targetTaskId")
    relationship_type = request.args.get("type")
    
    if source_task_id:
        filters["sourceTaskId"] = source_task_id
    if target_task_id:
        filters["targetTaskId"] = target_task_id
    if relationship_type:
        filters["type"] = relationship_type
        
    relationships = list(db.relationships.find(filters))
    
    # Convert ObjectId to string for JSON serialization
    for relationship in relationships:
        relationship["_id"] = str(relationship["_id"])
        
    return jsonify(relationships), 200

@relationships_bp.route("/relationships", methods=["POST"])
def create_relationship():
    """Create a new relationship between tasks"""
    print("Received relationship creation request")
    print(f"Request Content-Type: {request.headers.get('Content-Type')}")
    print(f"Request data: {request.get_data(as_text=True)}")
    
    db = get_db()
    data = request.json
    print(f"Parsed JSON data: {data}")
    
    # Add required timestamps as datetime objects for MongoDB
    now = datetime.utcnow()
    data["createdAt"] = now
    data["updatedAt"] = now
    
    # Convert string dates to datetime objects if they exist
    if isinstance(data.get("createdAt"), str):
        try:
            data["createdAt"] = datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00"))
        except ValueError:
            data["createdAt"] = now
    if isinstance(data.get("updatedAt"), str):
        try:
            data["updatedAt"] = datetime.fromisoformat(data["updatedAt"].replace("Z", "+00:00"))
        except ValueError:
            data["updatedAt"] = now
            
    # Convert task IDs to strings if they aren't already
    data["sourceTaskId"] = str(data["sourceTaskId"])
    data["targetTaskId"] = str(data["targetTaskId"])
    
    # Validate required fields
    required_fields = ["sourceTaskId", "targetTaskId", "type"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        print(f"Validation error - Missing fields: {missing_fields}")
        print(f"Received data: {data}")
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
    # Validate relationship type
    valid_types = ['blocks', 'blocked-by', 'relates-to', 'duplicates', 'parent-of', 'child-of']
    if data["type"] not in valid_types:
        print(f"Validation error - Invalid type: {data['type']}")
        print(f"Valid types are: {valid_types}")
        return jsonify({"error": f"Invalid relationship type. Must be one of: {', '.join(valid_types)}"}), 400
    
    # Check if tasks exist
    try:
        print(f"Looking up source task with ID: {data['sourceTaskId']}")
        print(f"Looking up target task with ID: {data['targetTaskId']}")
        
        try:
            source_task = db.tasks.find_one({"_id": ObjectId(data["sourceTaskId"])})
            print(f"Source task lookup result: {source_task}")
        except Exception as e:
            print(f"Error looking up source task: {str(e)}")
            return jsonify({"error": f"Invalid source task ID format: {str(e)}"}), 400
            
        try:
            target_task = db.tasks.find_one({"_id": ObjectId(data["targetTaskId"])})
            print(f"Target task lookup result: {target_task}")
        except Exception as e:
            print(f"Error looking up target task: {str(e)}")
            return jsonify({"error": f"Invalid target task ID format: {str(e)}"}), 400
        
        if not source_task:
            return jsonify({"error": f"Source task {data['sourceTaskId']} not found"}), 404
        if not target_task:
            return jsonify({"error": f"Target task {data['targetTaskId']} not found"}), 404
    except Exception as e:
        print(f"Unexpected error in task lookup: {str(e)}")
        return jsonify({"error": f"Error processing task lookup: {str(e)}"}), 400

    # Check for circular dependencies
    def find_dependencies(task_id, relationship_type, target_id, visited=None):
        if visited is None:
            visited = set()
        if task_id in visited:
            return False  # Already visited this path
        if task_id == target_id:
            return True  # Found path back to target
        visited.add(task_id)
        
        # Find all relationships where this task is the source
        relationships = db.relationships.find({
            "sourceTaskId": task_id,
            "type": relationship_type
        })
        
        for rel in relationships:
            if find_dependencies(rel["targetTaskId"], relationship_type, target_id, visited):
                return True
        return False

    # Check for circular dependency if relationship type is dependency-related
    if data["type"] in ["blocks", "blocked-by", "parent-of", "child-of"]:
        # For blocked-by and child-of, we need to check in reverse
        check_type = data["type"]
        check_source = data["sourceTaskId"]
        check_target = data["targetTaskId"]
        
        if data["type"] == "blocked-by":
            check_type = "blocks"
            check_source = data["targetTaskId"]
            check_target = data["sourceTaskId"]
        elif data["type"] == "child-of":
            check_type = "parent-of"
            check_source = data["targetTaskId"]
            check_target = data["sourceTaskId"]
        
        # First check if target already has a path to source
        if find_dependencies(check_target, check_type, check_source):
            return jsonify({
                "error": f"Creating this relationship would create a circular {check_type} dependency"
            }), 400
            
        # Then check if source would have a path to itself after adding this relationship
        temp_relationships = list(db.relationships.find({
            "type": check_type
        }))
        temp_relationships.append({
            "sourceTaskId": check_source,
            "targetTaskId": check_target,
            "type": check_type
        })
        
        visited = set()
        def check_cycle(current_id):
            if current_id in visited:
                return True
            visited.add(current_id)
            
            # Check all relationships where current task is the source
            for rel in temp_relationships:
                if rel["sourceTaskId"] == current_id:
                    if check_cycle(rel["targetTaskId"]):
                        return True
            visited.remove(current_id)
            return False
            
        if check_cycle(check_source):
            return jsonify({
                "error": f"Creating this relationship would create a circular {check_type} dependency"
            }), 400
    
    # Check for duplicate relationships
    existing = db.relationships.find_one({
        "sourceTaskId": data["sourceTaskId"],
        "targetTaskId": data["targetTaskId"],
        "type": data["type"]
    })
    
    if existing:
        return jsonify({"error": "Relationship already exists"}), 409
        
    try:
        print("Attempting to insert relationship with data:", data)
        result = db.relationships.insert_one(data)
        print("Successfully created relationship with ID:", result.inserted_id)
        return jsonify({"_id": str(result.inserted_id)}), 201
    except Exception as e:
        print("Error creating relationship:", str(e))
        print("Full error details:", e.__dict__)
        return jsonify({"error": str(e)}), 400

@relationships_bp.route("/relationships/<relationship_id>", methods=["PUT"])
def update_relationship(relationship_id):
    """Update an existing relationship"""
    db = get_db()
    data = request.json
    
    # Validate required fields
    required_fields = ["type"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
    # Validate relationship type
    valid_types = ['blocks', 'blocked-by', 'relates-to', 'duplicates', 'parent-of', 'child-of']
    if data["type"] not in valid_types:
        return jsonify({"error": f"Invalid relationship type. Must be one of: {', '.join(valid_types)}"}), 400
    
    try:
        # Add updated timestamp
        data["updatedAt"] = datetime.utcnow()
        
        # Get existing relationship to check for circular dependencies
        existing = db.relationships.find_one({"_id": ObjectId(relationship_id)})
        if not existing:
            return jsonify({"error": "Relationship not found"}), 404
            
        # Check for circular dependencies if changing to a dependency type
        if data["type"] in ["blocks", "blocked-by", "parent-of", "child-of"]:
            check_type = data["type"]
            check_source = existing["sourceTaskId"]
            check_target = existing["targetTaskId"]
            
            if data["type"] == "blocked-by":
                check_type = "blocks"
                check_source = existing["targetTaskId"]
                check_target = existing["sourceTaskId"]
            elif data["type"] == "child-of":
                check_type = "parent-of"
                check_source = existing["targetTaskId"]
                check_target = existing["sourceTaskId"]
            
            # Use the existing dependency check function
            def find_dependencies(task_id, relationship_type, target_id, visited=None):
                if visited is None:
                    visited = set()
                if task_id in visited:
                    return False
                if task_id == target_id:
                    return True
                visited.add(task_id)
                
                relationships = db.relationships.find({
                    "sourceTaskId": task_id,
                    "type": relationship_type
                })
                
                for rel in relationships:
                    if rel["_id"] != ObjectId(relationship_id) and find_dependencies(rel["targetTaskId"], relationship_type, target_id, visited):
                        return True
                return False
            
            if find_dependencies(check_target, check_type, check_source):
                return jsonify({
                    "error": f"Updating this relationship would create a circular {check_type} dependency"
                }), 400
        
        result = db.relationships.update_one(
            {"_id": ObjectId(relationship_id)},
            {"$set": data}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Relationship not found"}), 404
            
        return jsonify({"message": "Relationship updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@relationships_bp.route("/relationships/<relationship_id>", methods=["DELETE"])
def delete_relationship(relationship_id):
    """Delete a relationship"""
    db = get_db()
    
    try: 
        result = db.relationships.delete_one({"_id": ObjectId(relationship_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Relationship not found"}), 404
        return jsonify({"message": "Relationship deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
