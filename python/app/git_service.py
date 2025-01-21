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

@git_bp.route("/git/traffic/views/<repository>", methods=["GET"])
def get_repository_views(repository):
    """Get repository traffic views from GitHub API"""
    try:
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {current_app.config["GITHUB_TOKEN"]}'
        }
        url = f'https://api.github.com/repos/{repository}/traffic/views'
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Store traffic data in MongoDB
        db = get_db()
        traffic_data = response.json()
        traffic_data['repository'] = repository
        traffic_data['timestamp'] = datetime.utcnow()
        
        db.repository_traffic.update_one(
            {'repository': repository},
            {'$set': traffic_data},
            upsert=True
        )
        
        return jsonify(traffic_data), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch repository views: {str(e)}'}), 500

@git_bp.route("/git/traffic/clones/<repository>", methods=["GET"])
def get_repository_clones(repository):
    """Get repository clone counts from GitHub API"""
    try:
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {current_app.config["GITHUB_TOKEN"]}'
        }
        url = f'https://api.github.com/repos/{repository}/traffic/clones'
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Store clone data in MongoDB
        db = get_db()
        clone_data = response.json()
        clone_data['repository'] = repository
        clone_data['timestamp'] = datetime.utcnow()
        
        db.repository_clones.update_one(
            {'repository': repository},
            {'$set': clone_data},
            upsert=True
        )
        
        return jsonify(clone_data), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch repository clones: {str(e)}'}), 500

@git_bp.route("/git/traffic/stats/<repository>", methods=["GET"])
def get_traffic_stats(repository):
    """Get combined traffic statistics for a repository"""
    try:
        db = get_db()
        
        # Get latest traffic data
        views = db.repository_traffic.find_one({'repository': repository})
        clones = db.repository_clones.find_one({'repository': repository})
        
        if not views or not clones:
            # Fetch fresh data if not available
            views_response = requests.get(
                f'https://api.github.com/repos/{repository}/traffic/views',
                headers={
                    'Accept': 'application/vnd.github.v3+json',
                    'Authorization': f'token {current_app.config["GITHUB_TOKEN"]}'
                }
            )
            clones_response = requests.get(
                f'https://api.github.com/repos/{repository}/traffic/clones',
                headers={
                    'Accept': 'application/vnd.github.v3+json',
                    'Authorization': f'token {current_app.config["GITHUB_TOKEN"]}'
                }
            )
            
            views_response.raise_for_status()
            clones_response.raise_for_status()
            
            views = views_response.json()
            clones = clones_response.json()
            
            # Store fresh data
            views['repository'] = repository
            views['timestamp'] = datetime.utcnow()
            clones['repository'] = repository
            clones['timestamp'] = datetime.utcnow()
            
            db.repository_traffic.update_one(
                {'repository': repository},
                {'$set': views},
                upsert=True
            )
            db.repository_clones.update_one(
                {'repository': repository},
                {'$set': clones},
                upsert=True
            )
        
        # Combine stats
        stats = {
            'repository': repository,
            'views': views.get('count', 0),
            'unique_views': views.get('uniques', 0),
            'clones': clones.get('count', 0),
            'unique_clones': clones.get('uniques', 0),
            'views_history': views.get('views', []),
            'clones_history': clones.get('clones', []),
            'updated_at': max(
                views.get('timestamp', datetime.min),
                clones.get('timestamp', datetime.min)
            )
        }
        
        return jsonify(stats), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch traffic stats: {str(e)}'}), 500
