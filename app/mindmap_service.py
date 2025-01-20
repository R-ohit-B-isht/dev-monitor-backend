from flask import Blueprint, request, jsonify
from datetime import datetime
from .monitoring_service import get_db
from bson.objectid import ObjectId

mindmap_bp = Blueprint("mindmap", __name__)

@mindmap_bp.route("/mindmap/nodes", methods=["GET"])
def get_nodes():
    db = get_db()
    nodes = list(db.mindmap_nodes.find())
    for node in nodes:
        node["_id"] = str(node["_id"])
    return jsonify(nodes), 200

@mindmap_bp.route("/mindmap/nodes", methods=["POST"])
def create_node():
    db = get_db()
    data = request.json
    
    if not all(k in data for k in ["label", "position"]):
        return jsonify({"error": "Missing required fields"}), 400
        
    data["createdAt"] = datetime.utcnow()
    data["updatedAt"] = datetime.utcnow()
    
    result = db.mindmap_nodes.insert_one(data)
    return jsonify({"_id": str(result.inserted_id)}), 201

@mindmap_bp.route("/mindmap/nodes/<node_id>", methods=["DELETE"])
def delete_node(node_id):
    db = get_db()
    result = db.mindmap_nodes.delete_one({"_id": ObjectId(node_id)})
    
    if result.deleted_count == 0:
        return jsonify({"error": "Node not found"}), 404
        
    return jsonify({"message": "Node deleted"}), 200

@mindmap_bp.route("/mindmap/edges", methods=["GET"])
def get_edges():
    db = get_db()
    edges = list(db.mindmap_edges.find())
    for edge in edges:
        edge["_id"] = str(edge["_id"])
    return jsonify(edges), 200

@mindmap_bp.route("/mindmap/edges", methods=["POST"])
def create_edge():
    db = get_db()
    data = request.json
    
    if not all(k in data for k in ["sourceId", "targetId"]):
        return jsonify({"error": "Missing required fields"}), 400
        
    data["createdAt"] = datetime.utcnow()
    data["updatedAt"] = datetime.utcnow()
    
    result = db.mindmap_edges.insert_one(data)
    return jsonify({"_id": str(result.inserted_id)}), 201

@mindmap_bp.route("/mindmap/edges/<edge_id>", methods=["DELETE"])
def delete_edge(edge_id):
    db = get_db()
    result = db.mindmap_edges.delete_one({"_id": ObjectId(edge_id)})
    
    if result.deleted_count == 0:
        return jsonify({"error": "Edge not found"}), 404
        
    return jsonify({"message": "Edge deleted"}), 200
