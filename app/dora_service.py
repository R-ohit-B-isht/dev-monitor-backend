from flask import Blueprint, jsonify, request, current_app
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import json

dora_bp = Blueprint("dora", __name__)

# Initialize required collections on startup
def init_collections(db):
    """Ensure required collections exist with proper indexes"""
    # Deployments collection
    if 'deployments' not in db.list_collection_names():
        db.create_collection('deployments')
    db.deployments.create_index([('engineerId', 1), ('timestamp', -1)])
    db.deployments.create_index([('commitTime', 1)])
    
    # Incidents collection
    if 'incidents' not in db.list_collection_names():
        db.create_collection('incidents')
    db.incidents.create_index([('engineerId', 1), ('detectedAt', -1)])
    db.incidents.create_index([('status', 1)])
    
    # Git events collection
    if 'git_events' not in db.list_collection_names():
        db.create_collection('git_events')
    db.git_events.create_index([('engineerId', 1), ('timestamp', -1)])
    db.git_events.create_index([('eventType', 1)])

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

def _calculate_review_metrics(db, engineer_id, start_date, end_date):
    """Calculate code review related metrics"""
    try:
        pipeline = [
            {
                '$match': {
                    'engineerId': engineer_id,
                    'timestamp': {'$gte': start_date, '$lte': end_date},
                    'eventType': {'$in': ['review_started', 'review_completed', 'merged']}
                }
            },
            {
                '$group': {
                    '_id': '$taskId',
                    'reviewCount': {
                        '$sum': {
                            '$cond': [{'$eq': ['$eventType', 'review_started']}, 1, 0]
                        }
                    },
                    'mergeCount': {
                        '$sum': {
                            '$cond': [{'$eq': ['$eventType', 'merged']}, 1, 0]
                        }
                    },
                    'reviewDurations': {
                        '$push': {
                            '$cond': [
                                {'$eq': ['$eventType', 'review_completed']},
                                '$timestamp',
                                None
                            ]
                        }
                    }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'avgReviewsPerMerge': {
                        '$avg': {
                            '$divide': ['$reviewCount', {'$max': ['$mergeCount', 1]}]
                        }
                    },
                    'totalReviews': {'$sum': '$reviewCount'},
                    'totalMerges': {'$sum': '$mergeCount'}
                }
            }
        ]
        
        result = list(db.value_stream_events.aggregate(pipeline))
        if not result:
            return {
                'avgReviewsPerMerge': 0,
                'totalReviews': 0,
                'totalMerges': 0
            }
            
        metrics = result[0]
        metrics.pop('_id')
        return metrics
        
    except Exception as e:
        print(f"Error calculating review metrics: {str(e)}")
        return {
            'avgReviewsPerMerge': 0,
            'totalReviews': 0,
            'totalMerges': 0
        }

@dora_bp.route("/dora/metrics/<engineer_id>", methods=["GET"])
def get_dora_metrics(engineer_id):
    """Get all DORA metrics for the specified engineer and time period"""
    try:
        db = get_db()
        
        # Parse date range from query parameters
        try:
            end_date = datetime.fromisoformat(request.args.get('end_date', datetime.utcnow().isoformat()))
            days = int(request.args.get('days', '30'))
            branch = request.args.get('branch')
            start_date = end_date - timedelta(days=days)
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'Invalid date parameters: {str(e)}'}), 400
            
        metrics = {
            "deploymentFrequency": _calculate_deployment_frequency(db, engineer_id, start_date, end_date, branch),
            "leadTimeForChanges": _calculate_lead_time(db, engineer_id, start_date, end_date),
            "changeFailureRate": _calculate_failure_rate(db, engineer_id, start_date, end_date),
            "meanTimeToRecover": _calculate_mttr(db, engineer_id, start_date, end_date),
            "reviewMetrics": _calculate_review_metrics(db, engineer_id, start_date, end_date)
        }
        
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch DORA metrics: {str(e)}'}), 500
    
def _calculate_deployment_frequency(db, engineer_id, start_date, end_date, branch=None):
    """Calculate how often code is deployed to production, optionally filtered by branch"""
    try:
        query = {
            'engineerId': engineer_id,
            'timestamp': {'$gte': start_date, '$lte': end_date},
            'status': 'success'
        }
        
        if branch:
            query['gitMetadata.branch'] = branch
            
        deployments = db.deployments.count_documents(query)
        days = (end_date - start_date).days
        
        # Calculate frequency per day
        base_frequency = deployments / days if days > 0 else 0
        
        # If branch is specified, also get total deployments for comparison
        if branch:
            total_deployments = db.deployments.count_documents({
                'engineerId': engineer_id,
                'timestamp': {'$gte': start_date, '$lte': end_date},
                'status': 'success'
            })
            branch_percentage = (deployments / total_deployments * 100) if total_deployments > 0 else 0
            return {
                'frequency': base_frequency,
                'branchPercentage': branch_percentage,
                'totalDeployments': total_deployments,
                'branchDeployments': deployments
            }
            
        return base_frequency
    except Exception as e:
        print(f"Error calculating deployment frequency: {str(e)}")
        return 0
    
def _calculate_lead_time(db, engineer_id, start_date, end_date):
    """Calculate average time from commit to production deployment"""
    try:
        pipeline = [
            {
                '$match': {
                    'engineerId': engineer_id,
                    'deployedAt': {'$gte': start_date, '$lte': end_date},
                    'status': 'success'
                }
            },
            {
                '$project': {
                    'leadTime': {
                        '$subtract': ['$deployedAt', '$commitTime']
                    }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'averageLeadTime': {'$avg': '$leadTime'}
                }
            }
        ]
        
        result = list(db.deployments.aggregate(pipeline))
        return result[0]['averageLeadTime'] if result else 0
    except Exception as e:
        print(f"Error calculating lead time: {str(e)}")
        return 0
def _calculate_failure_rate(db, engineer_id, start_date, end_date):
    """Calculate percentage of deployments causing failures"""
    try:
        total_deployments = db.deployments.count_documents({
            'engineerId': engineer_id,
            'timestamp': {'$gte': start_date, '$lte': end_date}
        })
        
        failed_deployments = db.deployments.count_documents({
            'engineerId': engineer_id,
            'timestamp': {'$gte': start_date, '$lte': end_date},
            'status': 'failed'
        })
        
        return (failed_deployments / total_deployments * 100) if total_deployments > 0 else 0
    except Exception as e:
        print(f"Error calculating failure rate: {str(e)}")
        return 0
    
def _calculate_mttr(db, engineer_id, start_date, end_date):
    """Calculate Mean Time To Recovery from failures"""
    try:
        pipeline = [
            {
                '$match': {
                    'engineerId': engineer_id,
                    'resolvedAt': {'$gte': start_date, '$lte': end_date},
                    'status': 'resolved'
                }
            },
            {
                '$project': {
                    'recoveryTime': {
                        '$subtract': ['$resolvedAt', '$detectedAt']
                    }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'averageRecoveryTime': {'$avg': '$recoveryTime'}
                }
            }
        ]
        
        result = list(db.incidents.aggregate(pipeline))
        return result[0]['averageRecoveryTime'] if result else 0
    except Exception as e:
        print(f"Error calculating MTTR: {str(e)}")
        return 0
@dora_bp.route("/dora/deployments/<engineer_id>", methods=["POST"])
def record_deployment(engineer_id):
    """Record a new deployment event"""
    try:
        db = get_db()
        data = request.json
        
        if not data.get('commitTime'):
            return jsonify({'error': 'commitTime is required'}), 400
            
        deployment = {
            'engineerId': engineer_id,
            'timestamp': datetime.utcnow(),
            'commitTime': datetime.fromisoformat(data['commitTime']),
            'deployedAt': datetime.utcnow(),
            'status': data['status'],
            'metadata': data.get('metadata', {}),
            'sessionId': data.get('sessionId'),  # Track associated monitoring session
            'gitMetadata': {
                'commitHash': data.get('commitHash'),
                'branch': data.get('branch'),
                'repository': data.get('repository')
            }
        }
        
        result = db.deployments.insert_one(deployment)
        return jsonify({'deploymentId': str(result.inserted_id)}), 201
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to record deployment: {str(e)}'}), 500
    
@dora_bp.route("/dora/incidents/<engineer_id>", methods=["POST"])
def record_incident(engineer_id):
    """Record a new incident/failure"""
    try:
        db = get_db()
        data = request.json
        
        if not data.get('type') or not data.get('severity'):
            return jsonify({'error': 'type and severity are required'}), 400
            
        incident = {
            'engineerId': engineer_id,
            'detectedAt': datetime.utcnow(),
            'status': 'detected',
            'type': data['type'],
            'severity': data['severity'],
            'metadata': data.get('metadata', {}),
            'sessionId': data.get('sessionId'),  # Track associated monitoring session
            'deploymentId': data.get('deploymentId'),  # Link to related deployment if exists
            'affectedComponents': data.get('affectedComponents', []),
            'gitMetadata': {
                'commitHash': data.get('commitHash'),
                'branch': data.get('branch'),
                'repository': data.get('repository')
            }
        }
        
        result = db.incidents.insert_one(incident)
        return jsonify({'incidentId': str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({'error': f'Failed to record incident: {str(e)}'}), 500
    
@dora_bp.route("/dora/incidents/<incident_id>/resolve", methods=["POST"])
def resolve_incident(incident_id):
    """Mark an incident as resolved"""
    try:
        db = get_db()
        data = request.json or {}
        
        # Convert string ID to ObjectId
        try:
            incident_oid = ObjectId(incident_id)
        except Exception:
            return jsonify({'error': 'Invalid incident ID format'}), 400
            
        # Get current session ID if available
        session_id = data.get('sessionId')
        
        update_data = {
            'status': 'resolved',
            'resolvedAt': datetime.utcnow(),
            'resolution': data.get('resolution', ''),
            'resolvedBy': data.get('engineerId', 'unknown')
        }
        
        if session_id:
            update_data['resolutionSessionId'] = session_id
            
        result = db.incidents.update_one(
            {'_id': incident_oid},
            {'$set': update_data}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Incident not found'}), 404
            
        return jsonify({
            'message': 'Incident resolved',
            'incidentId': str(incident_id),
            'resolvedAt': update_data['resolvedAt'].isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to resolve incident: {str(e)}'}), 500
