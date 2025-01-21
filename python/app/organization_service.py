from flask import Blueprint, jsonify, request, current_app
from pymongo import MongoClient
from datetime import datetime, timedelta
import json
from .utils.anonymization import hash_engineer_id

org_bp = Blueprint("organization", __name__)

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

def aggregate_repository_metrics(db, repository, start_date, end_date):
    """Aggregate metrics for a single repository"""
    metrics = {
        'repository': repository,
        'activity': {
            'commits': 0,
            'pull_requests': 0,
            'reviews': 0,
            'comments': 0
        },
        'performance': {
            'avg_review_time': 0,
            'merge_success_rate': 0,
            'deployment_frequency': 0
        },
        'security': {
            'open_alerts': 0,
            'fixed_alerts': 0,
            'high_severity': 0
        },
        'collaboration': {
            'unique_contributors': 0,
            'review_coverage': 0,
            'comment_ratio': 0
        }
    }
    
    # Aggregate activity metrics
    activity = db.activity_feed.aggregate([
        {
            '$match': {
                'repository': repository,
                'timestamp': {'$gte': start_date, '$lt': end_date}
            }
        },
        {
            '$group': {
                '_id': None,
                'commits': {'$sum': {'$cond': [{'$eq': ['$type', 'commit']}, 1, 0]}},
                'pull_requests': {'$sum': {'$cond': [{'$eq': ['$type', 'pull_request']}, 1, 0]}},
                'reviews': {'$sum': {'$cond': [{'$eq': ['$type', 'review']}, 1, 0]}},
                'comments': {'$sum': {'$cond': [{'$eq': ['$type', 'comment']}, 1, 0]}},
                'unique_contributors': {'$addToSet': '$engineerId'}
            }
        }
    ]).next()
    
    metrics['activity'].update({
        'commits': activity.get('commits', 0),
        'pull_requests': activity.get('pull_requests', 0),
        'reviews': activity.get('reviews', 0),
        'comments': activity.get('comments', 0)
    })
    metrics['collaboration']['unique_contributors'] = len(activity.get('unique_contributors', []))
    
    # Calculate review coverage
    if activity.get('pull_requests', 0) > 0:
        metrics['collaboration']['review_coverage'] = (activity.get('reviews', 0) / activity['pull_requests']) * 100
    
    # Calculate comment ratio
    total_events = sum(metrics['activity'].values())
    if total_events > 0:
        metrics['collaboration']['comment_ratio'] = (activity.get('comments', 0) / total_events) * 100
    
    # Aggregate security metrics
    security = db.security_alerts.aggregate([
        {
            '$match': {
                'repository': repository,
                'created_at': {'$gte': start_date, '$lt': end_date}
            }
        },
        {
            '$group': {
                '_id': None,
                'open': {'$sum': {'$cond': [{'$eq': ['$state', 'open']}, 1, 0]}},
                'fixed': {'$sum': {'$cond': [{'$eq': ['$state', 'fixed']}, 1, 0]}},
                'high_severity': {'$sum': {'$cond': [{'$eq': ['$severity', 'high']}, 1, 0]}}
            }
        }
    ]).next()
    
    metrics['security'].update({
        'open_alerts': security.get('open', 0),
        'fixed_alerts': security.get('fixed', 0),
        'high_severity': security.get('high_severity', 0)
    })
    
    # Calculate performance metrics
    deployments = list(db.deployments.find({
        'repository': repository,
        'timestamp': {'$gte': start_date, '$lt': end_date}
    }))
    
    if deployments:
        success_count = sum(1 for d in deployments if d.get('status') == 'success')
        metrics['performance']['deployment_frequency'] = len(deployments) / ((end_date - start_date).days or 1)
        metrics['performance']['merge_success_rate'] = (success_count / len(deployments)) * 100
    
    return metrics

@org_bp.route("/org/aggregations", methods=["GET"])
def get_organization_metrics():
    """Get aggregated metrics across all repositories"""
    try:
        db = get_db()
        
        # Parse query parameters
        days = int(request.args.get('days', '30'))
        repositories = request.args.get('repositories', '').split(',')
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # If no repositories specified, get all unique repositories
        if not repositories or repositories == ['']:
            repositories = db.activity_feed.distinct('repository')
        
        # Aggregate metrics for each repository
        metrics = []
        for repo in repositories:
            repo_metrics = aggregate_repository_metrics(db, repo, start_date, end_date)
            metrics.append(repo_metrics)
        
        # Calculate organization-wide totals
        totals = {
            'total_repositories': len(metrics),
            'total_activity': sum(m['activity']['commits'] + m['activity']['pull_requests'] for m in metrics),
            'total_contributors': len(set().union(*[set(str(c) for c in m.get('collaboration', {}).get('unique_contributors', [])) for m in metrics])),
            'total_security_alerts': sum(m['security']['open_alerts'] + m['security']['fixed_alerts'] for m in metrics),
            'avg_deployment_frequency': sum(m['performance']['deployment_frequency'] for m in metrics) / len(metrics) if metrics else 0,
            'timeframe': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            }
        }
        
        return jsonify({
            'metrics': metrics,
            'totals': totals
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to aggregate organization metrics: {str(e)}'}), 500
