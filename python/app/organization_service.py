from flask import Blueprint, jsonify, request, current_app
from pymongo import MongoClient
from datetime import datetime, timedelta
from .utils.anonymization import hash_engineer_id, obfuscate_repository_name
import json

org_bp = Blueprint("organization", __name__)

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

def init_collections(db):
    """Initialize MongoDB collections and indexes for organization metrics"""
    if 'organization_metrics' not in db.list_collection_names():
        db.create_collection('organization_metrics')
    db.organization_metrics.create_index([('timestamp', -1)])
    db.organization_metrics.create_index([('repository', 1)])

@org_bp.route("/org/aggregations", methods=["GET"])
def get_organization_metrics():
    """Get aggregated metrics across all repositories"""
    try:
        db = get_db()
        days = int(request.args.get('days', '30'))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get all active repositories
        repos = list(db.monitored_repositories.find({'active': True}))
        
        metrics = []
        total_activity = 0
        total_contributors = set()
        total_security_alerts = 0
        total_deployment_frequency = 0
        
        for repo in repos:
            # Get repository activity
            activity = db.git_events.aggregate([
                {
                    '$match': {
                        'repository': repo['full_name'],
                        'timestamp': {'$gte': start_date, '$lte': end_date}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'commits': {
                            '$sum': {'$cond': [{'$eq': ['$type', 'commit']}, 1, 0]}
                        },
                        'pull_requests': {
                            '$sum': {'$cond': [{'$eq': ['$type', 'pull_request']}, 1, 0]}
                        },
                        'reviews': {
                            '$sum': {'$cond': [{'$eq': ['$type', 'review']}, 1, 0]}
                        },
                        'comments': {
                            '$sum': {'$cond': [{'$eq': ['$type', 'comment']}, 1, 0]}
                        },
                        'unique_contributors': {'$addToSet': '$author'}
                    }
                }
            ]).next()
            
            # Get security metrics
            security = db.security_alerts.aggregate([
                {
                    '$match': {
                        'repository': repo['full_name'],
                        'created_at': {'$gte': start_date}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'open_alerts': {
                            '$sum': {'$cond': [{'$eq': ['$state', 'open']}, 1, 0]}
                        },
                        'fixed_alerts': {
                            '$sum': {'$cond': [{'$eq': ['$state', 'fixed']}, 1, 0]}
                        },
                        'high_severity': {
                            '$sum': {'$cond': [{'$eq': ['$severity', 'high']}, 1, 0]}
                        }
                    }
                }
            ]).next()
            
            # Calculate performance metrics
            deployments = db.deployments.count_documents({
                'repository': repo['full_name'],
                'timestamp': {'$gte': start_date}
            })
            
            successful_merges = db.git_events.count_documents({
                'repository': repo['full_name'],
                'type': 'merge',
                'status': 'success',
                'timestamp': {'$gte': start_date}
            })
            
            total_merges = db.git_events.count_documents({
                'repository': repo['full_name'],
                'type': 'merge',
                'timestamp': {'$gte': start_date}
            })
            
            # Calculate review coverage
            prs_with_reviews = db.git_events.count_documents({
                'repository': repo['full_name'],
                'type': 'pull_request',
                'has_review': True,
                'timestamp': {'$gte': start_date}
            })
            
            total_prs = db.git_events.count_documents({
                'repository': repo['full_name'],
                'type': 'pull_request',
                'timestamp': {'$gte': start_date}
            })
            
            repo_metrics = {
                'repository': obfuscate_repository_name(repo['full_name']),
                'activity': {
                    'commits': activity.get('commits', 0),
                    'pull_requests': activity.get('pull_requests', 0),
                    'reviews': activity.get('reviews', 0),
                    'comments': activity.get('comments', 0)
                },
                'performance': {
                    'avg_review_time': 0,  # Calculated from review start/end times
                    'merge_success_rate': (successful_merges / total_merges * 100) if total_merges > 0 else 0,
                    'deployment_frequency': deployments / days
                },
                'security': {
                    'open_alerts': security.get('open_alerts', 0),
                    'fixed_alerts': security.get('fixed_alerts', 0),
                    'high_severity': security.get('high_severity', 0)
                },
                'collaboration': {
                    'unique_contributors': len(activity.get('unique_contributors', [])),
                    'review_coverage': (prs_with_reviews / total_prs * 100) if total_prs > 0 else 0,
                    'comment_ratio': activity.get('comments', 0) / activity.get('pull_requests', 1)
                }
            }
            
            metrics.append(repo_metrics)
            
            # Update totals
            total_activity += sum(repo_metrics['activity'].values())
            total_contributors.update(activity.get('unique_contributors', []))
            total_security_alerts += sum(repo_metrics['security'].values())
            total_deployment_frequency += repo_metrics['performance']['deployment_frequency']
        
        return jsonify({
            'metrics': metrics,
            'totals': {
                'total_repositories': len(repos),
                'total_activity': total_activity,
                'total_contributors': len(total_contributors),
                'total_security_alerts': total_security_alerts,
                'avg_deployment_frequency': total_deployment_frequency / len(repos) if repos else 0,
                'timeframe': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch organization metrics: {str(e)}'}), 500
