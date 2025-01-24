from flask import Blueprint, jsonify, request, current_app
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import requests
import json
import threading
import time
import os
from .utils.anonymization import hash_engineer_id, obfuscate_repository_name, obfuscate_email

security_bp = Blueprint("security", __name__)

def start_security_monitoring(app):
    """Start background thread for security monitoring"""
    def monitor_security():
        with app.app_context():
            while True:
                try:
                    db = get_db()
                    # Get list of repositories to monitor
                    repos = db.monitored_repositories.find({
                        'active': True
                    })
                    
                    for repo in repos:
                        try:
                            alerts = fetch_code_scanning_alerts(repo['full_name'])
                            
                            # Process and store alerts
                            for alert in alerts:
                                alert_doc = {
                                    'repository': obfuscate_repository_name(repo['full_name']),
                                    'alert_number': alert['number'],
                                    'state': alert['state'],
                                    'dismissed_reason': alert.get('dismissed_reason'),
                                    'dismissed_at': alert.get('dismissed_at'),
                                    'rule': alert['rule'],
                                    'severity': alert['rule'].get('severity'),
                                    'description': alert['rule'].get('description'),
                                    'location': alert.get('most_recent_instance', {}).get('location'),
                                    'commit_sha': alert.get('most_recent_instance', {}).get('commit_sha'),
                                    'created_at': datetime.strptime(alert['created_at'], '%Y-%m-%dT%H:%M:%SZ'),
                                    'updated_at': datetime.strptime(alert['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
                                }
                                
                                db.security_alerts.update_one(
                                    {
                                        'repository': repo['full_name'],
                                        'alert_number': alert['number']
                                    },
                                    {'$set': alert_doc},
                                    upsert=True
                                )
                        except Exception as e:
                            print(f"Error processing repository {repo['full_name']}: {str(e)}")
                            continue
                            
                except Exception as e:
                    print(f"Error in security monitoring thread: {str(e)}")
                
                # Sleep for 15 minutes before next check
                time.sleep(900)
    
    thread = threading.Thread(target=monitor_security, daemon=True)
    thread.start()
    return thread

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

def init_collections(db):
    """Ensure required collections exist with proper indexes"""
    if 'security_alerts' not in db.list_collection_names():
        db.create_collection('security_alerts')
    db.security_alerts.create_index([('created_at', -1)])
    db.security_alerts.create_index([('state', 1)])
    db.security_alerts.create_index([('severity', 1)])
    db.security_alerts.create_index([('repository', 1)])
    
    # Collection for repositories to monitor
    if 'monitored_repositories' not in db.list_collection_names():
        db.create_collection('monitored_repositories')
    db.monitored_repositories.create_index([('full_name', 1)], unique=True)
    db.monitored_repositories.create_index([('active', 1)])

def fetch_code_scanning_alerts(repository, state='open'):
    """Fetch code scanning alerts from GitHub API"""
    try:
        # Get token from environment directly as fallback
        github_token = current_app.config.get("GITHUB", {}).get("api_token") or os.environ.get("Github_Personal_Access_Token")
        
        if not github_token:
            print("Error: No GitHub token found in config or environment")
            return []
            
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'Bearer {github_token}'  # GitHub API v3 uses Bearer token
        }
        print("Debug: Checking GitHub token configuration")
        print(f"Debug: Token found: {'Yes' if github_token else 'No'}")
        print(f"Debug: Token prefix: {github_token[:10] if github_token else 'None'}...")
        
        # First verify repository access
        repo_url = f'https://api.github.com/repos/{repository}'
        try:
            # Verify token is valid first
            user_url = 'https://api.github.com/user'
            print(f"Checking GitHub token validity at: {user_url}")
            print(f"Full headers: {headers}")
            user_response = requests.get(user_url, headers=headers)
            print(f"User response status: {user_response.status_code}")
            print(f"User response body: {user_response.text}")
            
            if user_response.status_code == 401:
                print("GitHub authentication failed. Please check your token.")
                print(f"Current token from config: {current_app.config['GITHUB']['api_token']}")
                return []
                
            # Then check repository access
            print(f"Checking repository access: {repo_url}")
            repo_response = requests.get(repo_url, headers=headers)
            print(f"Repository response status: {repo_response.status_code}")
            
            if repo_response.status_code == 404:
                print(f"Repository {repository} not found")
                return []
            elif repo_response.status_code != 200:
                print(f"Error accessing repository: {repo_response.status_code}")
                print(f"Response body: {repo_response.text}")
                return []
                
            print("Repository access successful")
            
            # Then try to fetch code scanning alerts
            url = f'{repo_url}/code-scanning/alerts'
            params = {'state': state}
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return []
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 404:
            print(f"Code scanning not enabled for repository {repository}")
            return []
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching code scanning alerts: {str(e)}")
        return []

@security_bp.route("/security/alerts", methods=["GET"])
def get_security_alerts():
    """Get security alerts with optional filtering"""
    try:
        db = get_db()
        
        # Parse query parameters
        repository = request.args.get('repository')
        state = request.args.get('state', 'all')
        severity = request.args.get('severity')
        days = int(request.args.get('days', '30'))
        
        # Build query
        query = {}
        if repository:
            query['repository'] = repository
        if state != 'all':
            query['state'] = state
        if severity:
            query['severity'] = severity
        
        # Add date filter
        start_date = datetime.utcnow() - timedelta(days=days)
        query['created_at'] = {'$gte': start_date}
        
        # Fetch alerts from database
        alerts = list(db.security_alerts.find(query).sort('created_at', -1))
        
        # Convert ObjectId to string for JSON serialization
        for alert in alerts:
            alert['_id'] = str(alert['_id'])
            
        return jsonify({
            'alerts': alerts,
            'total': len(alerts),
            'open': sum(1 for a in alerts if a['state'] == 'open'),
            'fixed': sum(1 for a in alerts if a['state'] == 'fixed'),
            'dismissed': sum(1 for a in alerts if a['state'] == 'dismissed')
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch security alerts: {str(e)}'}), 500

@security_bp.route("/security/alerts/sync", methods=["POST"])
def sync_security_alerts():
    """Sync security alerts from GitHub"""
    try:
        db = get_db()
        data = request.json
        repository = data.get('repository')
        
        if not repository:
            return jsonify({'error': 'Repository parameter is required'}), 400
            
        # Fetch alerts from GitHub
        alerts = fetch_code_scanning_alerts(repository)
        
        # Process and store alerts
        for alert in alerts:
            alert_doc = {
                'repository': obfuscate_repository_name(repository),
                'alert_number': alert['number'],
                'state': alert['state'],
                'dismissed_reason': alert.get('dismissed_reason'),
                'dismissed_at': alert.get('dismissed_at'),
                'rule': alert['rule'],
                'severity': alert['rule'].get('severity'),
                'description': alert['rule'].get('description'),
                'location': alert.get('most_recent_instance', {}).get('location'),
                'commit_sha': alert.get('most_recent_instance', {}).get('commit_sha'),
                'created_at': datetime.strptime(alert['created_at'], '%Y-%m-%dT%H:%M:%SZ'),
                'updated_at': datetime.strptime(alert['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
            }
            
            # Update or insert alert
            db.security_alerts.update_one(
                {
                    'repository': repository,
                    'alert_number': alert['number']
                },
                {'$set': alert_doc},
                upsert=True
            )
            
        return jsonify({
            'message': 'Security alerts synced successfully',
            'count': len(alerts)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to sync security alerts: {str(e)}'}), 500

@security_bp.route("/security/alerts/stats", methods=["GET"])
def get_security_stats():
    """Get security alert statistics"""
    try:
        db = get_db()
        repository = request.args.get('repository')
        days = int(request.args.get('days', '30'))
        
        # Build base query
        match_query = {}
        if repository:
            match_query['repository'] = repository
            
        # Add date filter
        start_date = datetime.utcnow() - timedelta(days=days)
        match_query['created_at'] = {'$gte': start_date}
        
        # Aggregate statistics
        pipeline = [
            {'$match': match_query},
            {
                '$group': {
                    '_id': None,
                    'total': {'$sum': 1},
                    'open': {
                        '$sum': {'$cond': [{'$eq': ['$state', 'open']}, 1, 0]}
                    },
                    'fixed': {
                        '$sum': {'$cond': [{'$eq': ['$state', 'fixed']}, 1, 0]}
                    },
                    'dismissed': {
                        '$sum': {'$cond': [{'$eq': ['$state', 'dismissed']}, 1, 0]}
                    },
                    'high_severity': {
                        '$sum': {'$cond': [{'$eq': ['$severity', 'high']}, 1, 0]}
                    },
                    'medium_severity': {
                        '$sum': {'$cond': [{'$eq': ['$severity', 'medium']}, 1, 0]}
                    },
                    'low_severity': {
                        '$sum': {'$cond': [{'$eq': ['$severity', 'low']}, 1, 0]}
                    }
                }
            }
        ]
        
        result = list(db.security_alerts.aggregate(pipeline))
        stats = result[0] if result else {
            'total': 0,
            'open': 0,
            'fixed': 0,
            'dismissed': 0,
            'high_severity': 0,
            'medium_severity': 0,
            'low_severity': 0
        }
        
        if '_id' in stats:
            stats.pop('_id')
            
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch security statistics: {str(e)}'}), 500
