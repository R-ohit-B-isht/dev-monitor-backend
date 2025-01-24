from flask import Blueprint, jsonify, request, current_app
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import json
from .utils.anonymization import hash_engineer_id, obfuscate_repository_name, obfuscate_commit_message, obfuscate_email
import requests

git_bp = Blueprint("git", __name__)

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

@git_bp.route("/git/events", methods=["POST"])
def record_git_event():
    """Record a new git event (commit, push, merge, etc.)"""
    db = get_db()
    data = request.json
    
    event = {
        'timestamp': datetime.utcnow(),
        'type': data['type'],  # commit, push, merge
        'sha': data['sha'],
        'taskId': ObjectId(data['taskId']) if data.get('taskId') else None,
        'author': obfuscate_email(data.get('author')),
        'message': obfuscate_commit_message(data.get('message', '')),
        'branch': data.get('branch'),
        'repository': obfuscate_repository_name(data.get('repository', '')),
        'metadata': data.get('metadata', {})
    }
    
    result = db.git_events.insert_one(event)
    return jsonify({'eventId': str(result.inserted_id)}), 201

@git_bp.route("/git/events/<task_id>", methods=["GET"])
def get_git_events(task_id):
    """Get all git events for a specific task"""
    db = get_db()
    events = list(db.git_events.find({'taskId': ObjectId(task_id)}))
    
    # Convert ObjectId to string for JSON serialization
    for event in events:
        event['_id'] = str(event['_id'])
        event['taskId'] = str(event['taskId']) if event['taskId'] else None
        
    return jsonify(events), 200

@git_bp.route("/git/deployments", methods=["POST"])
def record_deployment():
    """Record a new deployment event"""
    db = get_db()
    data = request.json
    
    deployment = {
        'timestamp': datetime.utcnow(),
        'taskId': ObjectId(data['taskId']) if data.get('taskId') else None,
        'sha': data['sha'],
        'environment': data['environment'],  # dev, staging, prod
        'status': data['status'],  # success, failed
        'deployer': data.get('deployer'),
        'metadata': data.get('metadata', {})
    }
    
    result = db.deploy_events.insert_one(deployment)
    return jsonify({'deploymentId': str(result.inserted_id)}), 201

@git_bp.route("/git/deployments/<task_id>", methods=["GET"])
def get_deployments(task_id):
    """Get all deployments for a specific task"""
    db = get_db()
    deployments = list(db.deploy_events.find({'taskId': ObjectId(task_id)}))
    
    # Convert ObjectId to string for JSON serialization
    for deployment in deployments:
        deployment['_id'] = str(deployment['_id'])
        deployment['taskId'] = str(deployment['taskId']) if deployment['taskId'] else None
        
    return jsonify(deployments), 200

@git_bp.route("/git/metrics/<task_id>", methods=["GET"])
def get_git_metrics(task_id):
    """Get git-related metrics for a specific task"""
    db = get_db()
    
    # Get all git events for the task
    git_events = list(db.git_events.find({'taskId': ObjectId(task_id)}))
    
    # Get all deployments for the task
    deployments = list(db.deploy_events.find({'taskId': ObjectId(task_id)}))
    
    metrics = {
        'commitCount': len([e for e in git_events if e['type'] == 'commit']),
        'pushCount': len([e for e in git_events if e['type'] == 'push']),
        'mergeCount': len([e for e in git_events if e['type'] == 'merge']),
        'deploymentCount': len(deployments),
        'successfulDeployments': len([d for d in deployments if d['status'] == 'success']),
        'failedDeployments': len([d for d in deployments if d['status'] == 'failed'])
    }
    
    return jsonify(metrics), 200
