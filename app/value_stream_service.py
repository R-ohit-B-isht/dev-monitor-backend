from flask import Blueprint, jsonify, request, current_app
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import json
from .utils.anonymization import hash_engineer_id

value_stream_bp = Blueprint("value_stream", __name__)

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

def calculate_cycle_time(events):
    """Calculate cycle time from code start to review completion"""
    if not events:
        return 0
        
    # Sort events by createdAt
    sorted_events = sorted(events, key=lambda x: x['createdAt'])
    
    # Find first code_started and last review_completed
    code_start = None
    review_end = None
    
    for event in sorted_events:
        if event['eventType'] == 'code_started' and not code_start:
            code_start = event['createdAt']
        elif event['eventType'] == 'review_completed':
            review_end = event['createdAt']
            
    # If missing either event, use first and last events
    if not code_start and not review_end and len(sorted_events) >= 2:
        code_start = sorted_events[0]['createdAt']
        review_end = sorted_events[-1]['createdAt']
    elif not code_start and review_end:
        code_start = sorted_events[0]['createdAt']
    elif code_start and not review_end:
        review_end = sorted_events[-1]['createdAt']
    elif not code_start or not review_end:
        return 0
        
    cycle_time = (review_end - code_start).total_seconds() / 3600  # Convert to hours
    return cycle_time

def calculate_lead_time(events):
    """Calculate lead time from task creation to deployment"""
    if not events:
        return 0
        
    # Sort events by createdAt
    sorted_events = sorted(events, key=lambda x: x['createdAt'])
    
    # Find first task_created and first deployed
    task_created = None
    deployed = None
    
    for event in sorted_events:
        if event['eventType'] == 'task_created' and not task_created:
            task_created = event['createdAt']
        elif event['eventType'] == 'deployed' and not deployed:
            deployed = event['createdAt']
            
    if not task_created or not deployed:
        return 0
        
    lead_time = (deployed - task_created).total_seconds() / 3600  # Convert to hours
    return lead_time

def init_collections(db):
    """Ensure required collections exist with proper indexes"""
    # Value stream events collection
    if 'value_stream_events' not in db.list_collection_names():
        db.create_collection('value_stream_events')
    db.value_stream_events.create_index([('engineerId', 1), ('createdAt', -1)])
    db.value_stream_events.create_index([('taskId', 1)])
    db.value_stream_events.create_index([('eventType', 1)])

@value_stream_bp.route("/value-stream/metrics/<engineer_id>", methods=["GET"])
def get_value_stream_metrics(engineer_id):
    """Get value stream metrics for tasks from idea to deployment"""
    try:
        db = get_db()
        print(f"Processing value stream metrics for engineer: {engineer_id}")
        
        # Parse date range from query parameters
        try:
            end_date = datetime.fromisoformat(request.args.get('end_date', datetime.utcnow().isoformat()))
            days = int(request.args.get('days', '30'))
            start_date = end_date - timedelta(days=days)
            print(f"Date range: {start_date} to {end_date}")
        except (ValueError, TypeError) as e:
            print(f"Date parsing error: {str(e)}")
            return jsonify({'error': f'Invalid date parameters: {str(e)}'}), 400
            
        # Aggregate value stream metrics
        pipeline = [
            {
                '$match': {
                    'engineerId': hash_engineer_id(engineer_id),
                    'createdAt': {'$gte': start_date, '$lte': end_date}
                }
            },
            {
                '$lookup': {
                    'from': 'value_stream_events',
                    'let': { 'task_id': '$_id' },
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$taskId', '$$task_id']
                                }
                            }
                        },
                        {
                            '$sort': { 'createdAt': 1 }
                        }
                    ],
                    'as': 'events'
                }
            },
            {
                '$project': {
                    'title': 1,
                    'status': 1,
                    'ideaToCode': {
                        '$let': {
                            'vars': {
                                'codeStartEvent': {
                                    '$filter': {
                                        'input': '$events',
                                        'cond': {'$eq': ['$$this.eventType', 'code_started']}
                                    }
                                }
                            },
                            'in': {
                                '$cond': {
                                    'if': {'$gt': [{'$size': '$$codeStartEvent'}, 0]},
                                    'then': {
                                        '$divide': [
                                            {'$subtract': [
                                                {'$arrayElemAt': ['$$codeStartEvent.createdAt', 0]},
                                                '$createdAt'
                                            ]},
                                            3600000  # Convert milliseconds to hours
                                        ]
                                    },
                                    'else': 0
                                }
                            }
                        }
                    },
                    'codeToReview': {
                        '$let': {
                            'vars': {
                                'reviewStartEvent': {
                                    '$filter': {
                                        'input': '$events',
                                        'cond': {'$eq': ['$$this.eventType', 'review_started']}
                                    }
                                },
                                'codeCompleteEvent': {
                                    '$filter': {
                                        'input': '$events',
                                        'cond': {'$eq': ['$$this.eventType', 'code_completed']}
                                    }
                                }
                            },
                            'in': {
                                '$cond': {
                                    'if': {'$and': [
                                        {'$gt': [{'$size': '$$reviewStartEvent'}, 0]},
                                        {'$gt': [{'$size': '$$codeCompleteEvent'}, 0]}
                                    ]},
                                    'then': {
                                        '$divide': [
                                            {'$subtract': [
                                                {'$arrayElemAt': ['$$reviewStartEvent.createdAt', 0]},
                                                {'$arrayElemAt': ['$$codeCompleteEvent.createdAt', 0]}
                                            ]},
                                            3600000
                                        ]
                                    },
                                    'else': 0
                                }
                            }
                        }
                    },
                    'reviewToMerge': {
                        '$let': {
                            'vars': {
                                'mergeEvent': {
                                    '$filter': {
                                        'input': '$events',
                                        'cond': {'$eq': ['$$this.eventType', 'merged']}
                                    }
                                },
                                'reviewCompleteEvent': {
                                    '$filter': {
                                        'input': '$events',
                                        'cond': {'$eq': ['$$this.eventType', 'review_completed']}
                                    }
                                }
                            },
                            'in': {
                                '$cond': {
                                    'if': {'$and': [
                                        {'$gt': [{'$size': '$$mergeEvent'}, 0]},
                                        {'$gt': [{'$size': '$$reviewCompleteEvent'}, 0]}
                                    ]},
                                    'then': {
                                        '$divide': [
                                            {'$subtract': [
                                                {'$arrayElemAt': ['$$mergeEvent.createdAt', 0]},
                                                {'$arrayElemAt': ['$$reviewCompleteEvent.createdAt', 0]}
                                            ]},
                                            3600000
                                        ]
                                    },
                                    'else': 0
                                }
                            }
                        }
                    },
                    'mergeToDeploy': {
                        '$let': {
                            'vars': {
                                'deployEvent': {
                                    '$filter': {
                                        'input': '$events',
                                        'cond': {'$eq': ['$$this.eventType', 'deployed']}
                                    }
                                },
                                'mergeEvent': {
                                    '$filter': {
                                        'input': '$events',
                                        'cond': {'$eq': ['$$this.eventType', 'merged']}
                                    }
                                }
                            },
                            'in': {
                                '$cond': {
                                    'if': {'$and': [
                                        {'$gt': [{'$size': '$$deployEvent'}, 0]},
                                        {'$gt': [{'$size': '$$mergeEvent'}, 0]}
                                    ]},
                                    'then': {
                                        '$divide': [
                                            {'$subtract': [
                                                {'$arrayElemAt': ['$$deployEvent.createdAt', 0]},
                                                {'$arrayElemAt': ['$$mergeEvent.createdAt', 0]}
                                            ]},
                                            3600000
                                        ]
                                    },
                                    'else': 0
                                }
                            }
                        }
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
        
        print("Executing MongoDB pipeline...")
        try:
            result = list(db.tasks.aggregate(pipeline))
            print(f"Pipeline result: {json.dumps(result, default=str)}")
            print("Checking task events:")
            events = list(db.value_stream_events.find({}))
            print(f"All events: {json.dumps(events, default=str)}")
            
            if not result:
                print("No results from pipeline")
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
            
            # Convert ObjectId to string in tasks
            for task in tasks:
                task['_id'] = str(task['_id'])
            
            return jsonify({
                'metrics': metrics,
                'tasks': tasks
            }), 200
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error executing MongoDB pipeline: {str(e)}\n{error_details}")
            return jsonify({'error': f'Failed to execute MongoDB pipeline: {str(e)}'}), 500
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error fetching value stream metrics: {str(e)}\n{error_details}")
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
            'engineerId': hash_engineer_id(engineer_id),
            'taskId': data['taskId'] if isinstance(data['taskId'], ObjectId) else ObjectId(data['taskId']),
            'eventType': data['eventType'],
            'createdAt': datetime.utcnow(),
            'metadata': data.get('metadata', {}),
            'sessionId': data.get('sessionId')
        }
        
        result = db.value_stream_events.insert_one(event)
        return jsonify({'eventId': str(result.inserted_id)}), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to record value stream event: {str(e)}'}), 500
