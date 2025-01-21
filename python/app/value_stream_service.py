from flask import Blueprint, jsonify, request, current_app
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import json

value_stream_bp = Blueprint("value_stream", __name__)

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

def init_collections(db):
    """Ensure required collections exist with proper indexes"""
    # Value stream events collection
    if 'value_stream_events' not in db.list_collection_names():
        db.create_collection('value_stream_events')
    db.value_stream_events.create_index([('engineerId', 1), ('timestamp', -1)])
    db.value_stream_events.create_index([('taskId', 1)])
    db.value_stream_events.create_index([('eventType', 1)])

@value_stream_bp.route("/value-stream/metrics/<engineer_id>", methods=["GET"])
def get_value_stream_metrics(engineer_id):
    """Get value stream metrics for tasks from idea to deployment"""
    try:
        db = get_db()
        
        # Parse date range from query parameters
        try:
            end_date = datetime.fromisoformat(request.args.get('end_date', datetime.utcnow().isoformat()))
            days = int(request.args.get('days', '30'))
            start_date = end_date - timedelta(days=days)
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'Invalid date parameters: {str(e)}'}), 400
            
        # Aggregate value stream metrics
        pipeline = [
            {
                '$match': {
                    'engineerId': engineer_id,
                    'createdAt': {'$gte': start_date, '$lte': end_date}
                }
            },
            {
                '$lookup': {
                    'from': 'value_stream_events',
                    'localField': '_id',
                    'foreignField': 'taskId',
                    'as': 'events'
                }
            },
            {
                '$project': {
                    'title': 1,
                    'status': 1,
                    'ideaToCode': {
                        '$subtract': [
                            {'$min': {'$filter': {
                                'input': '$events',
                                'cond': {'$eq': ['$$this.eventType', 'code_started']}
                            }}},
                            '$createdAt'
                        ]
                    },
                    'codeToReview': {
                        '$subtract': [
                            {'$min': {'$filter': {
                                'input': '$events',
                                'cond': {'$eq': ['$$this.eventType', 'review_started']}
                            }}},
                            {'$min': {'$filter': {
                                'input': '$events',
                                'cond': {'$eq': ['$$this.eventType', 'code_completed']}
                            }}}
                        ]
                    },
                    'reviewToMerge': {
                        '$subtract': [
                            {'$min': {'$filter': {
                                'input': '$events',
                                'cond': {'$eq': ['$$this.eventType', 'merged']}
                            }}},
                            {'$min': {'$filter': {
                                'input': '$events',
                                'cond': {'$eq': ['$$this.eventType', 'review_completed']}
                            }}}
                        ]
                    },
                    'mergeToDeploy': {
                        '$subtract': [
                            {'$min': {'$filter': {
                                'input': '$events',
                                'cond': {'$eq': ['$$this.eventType', 'deployed']}
                            }}},
                            {'$min': {'$filter': {
                                'input': '$events',
                                'cond': {'$eq': ['$$this.eventType', 'merged']}
                            }}}
                        ]
                    }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'avgIdeaToCode': {'$avg': '$ideaToCode'},
                    'avgCodeToReview': {'$avg': '$codeToReview'},
                    'avgReviewToMerge': {'$avg': '$reviewToMerge'},
                    'avgMergeToDeploy': {'$avg': '$mergeToDeploy'},
                    'totalTasks': {'$sum': 1},
                    'inProgressTasks': {
                        '$sum': {
                            '$cond': [
                                {'$in': ['$status', ['In-Progress', 'Review']]},
                                1,
                                0
                            ]
                        }
                    },
                    'doneTasks': {
                        '$sum': {
                            '$cond': [
                                {'$eq': ['$status', 'Done']},
                                1,
                                0
                            ]
                        }
                    },
                    'tasks': {'$push': '$$ROOT'}
                }
            }
        ]
        
        result = list(db.tasks.aggregate(pipeline))
        
        if not result:
            return jsonify({
                'metrics': {
                    'avgIdeaToCode': 0,
                    'avgCodeToReview': 0,
                    'avgReviewToMerge': 0,
                    'avgMergeToDeploy': 0
                },
                'tasks': []
            }), 200
            
        metrics = result[0]
        tasks = metrics.pop('tasks')
        metrics.pop('_id')
        
        return jsonify({
            'metrics': metrics,
            'tasks': tasks
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch value stream metrics: {str(e)}'}), 500

@value_stream_bp.route("/value-stream/events/<engineer_id>", methods=["POST"])
def record_value_stream_event(engineer_id):
    """Record a new value stream event"""
    try:
        db = get_db()
        data = request.json
        
        if not data.get('taskId') or not data.get('eventType'):
            return jsonify({'error': 'taskId and eventType are required'}), 400
            
        # Validate event type
        valid_event_types = [
            'code_started', 'code_completed',
            'review_started', 'review_completed',
            'merged', 'deployed'
        ]
        
        if data['eventType'] not in valid_event_types:
            return jsonify({'error': f'Invalid event type. Must be one of: {", ".join(valid_event_types)}'}), 400
            
        event = {
            'engineerId': engineer_id,
            'taskId': ObjectId(data['taskId']),
            'eventType': data['eventType'],
            'timestamp': datetime.utcnow(),
            'metadata': data.get('metadata', {}),
            'sessionId': data.get('sessionId')
        }
        
        result = db.value_stream_events.insert_one(event)
        return jsonify({'eventId': str(result.inserted_id)}), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to record value stream event: {str(e)}'}), 500
