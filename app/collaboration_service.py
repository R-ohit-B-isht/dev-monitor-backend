from flask import Blueprint, jsonify, request, current_app
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import json

collab_bp = Blueprint("collaboration", __name__)

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

def init_collections(db):
    """Initialize MongoDB collections and indexes for collaboration data"""
    if 'activity_feed' not in db.list_collection_names():
        db.create_collection('activity_feed')
    db.activity_feed.create_index([('timestamp', -1)])
    db.activity_feed.create_index([('engineerId', 1)])
    db.activity_feed.create_index([('eventType', 1)])
    db.activity_feed.create_index([('repository', 1)])

@collab_bp.route("/collab/activity", methods=["GET"])
def get_activity_feed():
    """Get activity feed with optional filtering"""
    try:
        db = get_db()
        
        # Parse query parameters
        engineer_id = request.args.get('engineerId')
        repository = request.args.get('repository')
        event_type = request.args.get('eventType')
        days = int(request.args.get('days', '30'))
        
        # Build query
        query = {}
        if engineer_id:
            query['engineerId'] = engineer_id
        if repository:
            query['repository'] = repository
        if event_type:
            query['eventType'] = event_type
            
        # Add date filter
        start_date = datetime.utcnow() - timedelta(days=days)
        query['timestamp'] = {'$gte': start_date}
        
        # Fetch activity feed
        activities = list(db.activity_feed.find(query).sort('timestamp', -1))
        
        # Convert ObjectId to string for JSON serialization
        for activity in activities:
            activity['_id'] = str(activity['_id'])
            
        return jsonify({
            'activities': activities,
            'total': len(activities)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch activity feed: {str(e)}'}), 500

@collab_bp.route("/collab/activity", methods=["POST"])
def record_activity():
    """Record a new activity event"""
    try:
        db = get_db()
        data = request.json
        
        required_fields = ['engineerId', 'eventType', 'repository']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        activity = {
            'engineerId': data['engineerId'],
            'eventType': data['eventType'],
            'repository': data['repository'],
            'timestamp': datetime.utcnow(),
            'metadata': data.get('metadata', {}),
            'title': data.get('title'),
            'description': data.get('description'),
            'url': data.get('url'),
            'reviewers': data.get('reviewers', []),
            'commentCount': data.get('commentCount', 0),
            'additions': data.get('additions', 0),
            'deletions': data.get('deletions', 0)
        }
        
        result = db.activity_feed.insert_one(activity)
        return jsonify({'activityId': str(result.inserted_id)}), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to record activity: {str(e)}'}), 500

@collab_bp.route("/collab/stats", methods=["GET"])
def get_collaboration_stats():
    """Get collaboration statistics"""
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
        match_query['timestamp'] = {'$gte': start_date}
        
        # Aggregate statistics
        pipeline = [
            {'$match': match_query},
            {
                '$group': {
                    '_id': None,
                    'total_reviews': {
                        '$sum': {'$cond': [{'$eq': ['$eventType', 'review']}, 1, 0]}
                    },
                    'total_comments': {'$sum': '$commentCount'},
                    'total_additions': {'$sum': '$additions'},
                    'total_deletions': {'$sum': '$deletions'},
                    'unique_reviewers': {'$addToSet': '$engineerId'},
                    'event_types': {'$addToSet': '$eventType'}
                }
            }
        ]
        
        result = list(db.activity_feed.aggregate(pipeline))
        stats = result[0] if result else {
            'total_reviews': 0,
            'total_comments': 0,
            'total_additions': 0,
            'total_deletions': 0,
            'unique_reviewers': [],
            'event_types': []
        }
        
        if '_id' in stats:
            stats.pop('_id')
            
        # Add reviewer count
        stats['reviewer_count'] = len(stats['unique_reviewers'])
        stats['unique_reviewers'] = list(stats['unique_reviewers'])
            
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch collaboration statistics: {str(e)}'}), 500
