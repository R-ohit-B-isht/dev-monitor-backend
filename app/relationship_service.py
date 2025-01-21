from flask import Blueprint, request, jsonify
from datetime import datetime
from .monitoring_service import get_db
from bson.objectid import ObjectId

relationships_bp = Blueprint("relationships", __name__)

@relationships_bp.route("/relationships", methods=["GET"])
def get_relationships():
    db = get_db()
    filters = {}
    
    source_task_id = request.args.get("sourceTaskId")
    target_task_id = request.args.get("targetTaskId")
    rel_type = request.args.get("type")
    
    if source_task_id:
        filters["sourceTaskId"] = source_task_id
    if target_task_id:
        filters["targetTaskId"] = target_task_id
    if rel_type:
        filters["type"] = rel_type
        
    relationships = list(db.relationships.find(filters))
    for rel in relationships:
        rel["_id"] = str(rel["_id"])
        
    return jsonify(relationships), 200

@relationships_bp.route("/relationships", methods=["POST"])
def create_relationship():
    db = get_db()
    data = request.json
    
    required_fields = ["sourceTaskId", "targetTaskId", "type"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
        
    data["createdAt"] = datetime.utcnow()
    data["updatedAt"] = datetime.utcnow()
    
    result = db.relationships.insert_one(data)
    return jsonify({"_id": str(result.inserted_id)}), 201

@relationships_bp.route("/relationships/<relationship_id>", methods=["PUT"])
def update_relationship(relationship_id):
    db = get_db()
    data = request.json
    
    if "type" not in data:
        return jsonify({"error": "Type is required"}), 400
        
    result = db.relationships.update_one(
        {"_id": ObjectId(relationship_id)},
        {
            "$set": {
                "type": data["type"],
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        return jsonify({"error": "Relationship not found"}), 404
        
    return jsonify({"message": "Relationship updated"}), 200

@relationships_bp.route("/relationships/<relationship_id>", methods=["DELETE"])
def delete_relationship(relationship_id):
    db = get_db()
    result = db.relationships.delete_one({"_id": ObjectId(relationship_id)})
    
    if result.deleted_count == 0:
        return jsonify({"error": "Relationship not found"}), 404
        
    return jsonify({"message": "Relationship deleted"}), 200
