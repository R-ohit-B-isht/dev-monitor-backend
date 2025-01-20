from flask import Blueprint, jsonify, request, current_app
from pymongo import MongoClient
from datetime import datetime, timedelta
import json

monitoring_bp = Blueprint("monitoring", __name__)

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

@monitoring_bp.route("/monitoring/focus-metrics/current", methods=["GET"])
def get_focus_metrics():
    db = get_db()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get today's monitoring sessions
    sessions = list(db.monitoring_sessions.find({
        'engineerId': 'current',
        'startTime': {'$gte': today},
        'status': {'$in': ['stopped', 'idle']}
    }))
    
    total_focus_time = sum(s.get('focusTime', 0) for s in sessions)
    total_time = sum((s.get('focusTime', 0) + s.get('idleTime', 0)) for s in sessions)
    focus_percentage = (total_focus_time / total_time * 100) if total_time > 0 else 0
    
    # Get activity counts
    activities = list(db.activity_events.find({
        'engineerId': 'current',
        'timestamp': {'$gte': today}
    }))
    
    focus_activities = len([a for a in activities if a['eventType'] in ['keyboard', 'mouse', 'ide']])
    
    # Calculate productivity score (60% focus time, 40% activity type)
    productivity_score = (0.6 * focus_percentage) + (0.4 * (focus_activities / len(activities) * 100)) if activities else 0
    
    # Get new badges earned today
    new_badges = [a['badge'] for a in db.achievements.find({
        'engineerId': 'current',
        'earnedAt': {'$gte': today}
    })]
    
    return jsonify({
        'focusTimeSeconds': total_focus_time,
        'focusTimePercentage': focus_percentage,
        'totalActivities': len(activities),
        'focusActivities': focus_activities,
        'focusActivityRatio': focus_activities / len(activities) if activities else 0,
        'productivityScore': productivity_score,
        'newBadges': new_badges
    }), 200

@monitoring_bp.route("/monitoring/start-time", methods=["POST"])
def start_time_tracking():
    db = get_db()
    data = request.json
    
    session = {
        'engineerId': data['engineerId'],
        'startTime': datetime.utcnow(),
        'status': 'running',
        'focusTime': 0,
        'idleTime': 0
    }
    
    result = db.monitoring_sessions.insert_one(session)
    return jsonify({'sessionId': str(result.inserted_id)}), 201

@monitoring_bp.route("/monitoring/stop-time", methods=["POST"])
def stop_time_tracking():
    db = get_db()
    data = request.json
    
    session = db.monitoring_sessions.find_one_and_update(
        {'_id': data['sessionId'], 'status': 'running'},
        {
            '$set': {
                'status': 'stopped',
                'endTime': datetime.utcnow()
            }
        }
    )
    
    if not session:
        return jsonify({'error': 'Session not found or already stopped'}), 404
        
    duration = (datetime.utcnow() - session['startTime']).total_seconds()
    return jsonify({'duration': duration}), 200

@monitoring_bp.route("/monitoring/activity", methods=["POST"])
def record_activity():
    db = get_db()
    data = request.json
    
    event = {
        'engineerId': data['engineerId'],
        'sessionId': data['sessionId'],
        'timestamp': datetime.utcnow(),
        'eventType': data['eventType'],
        'metadata': data.get('metadata', {})
    }
    
    db.activity_events.insert_one(event)
    return jsonify({'message': 'Activity recorded'}), 201

@monitoring_bp.route("/monitoring/achievements/current", methods=["GET"])
def get_achievements():
    db = get_db()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    achievements = list(db.achievements.find({
        'engineerId': 'current',
        'earnedAt': {'$gte': today}
    }))
    
    # Convert ObjectId to string for JSON serialization
    for achievement in achievements:
        achievement['_id'] = str(achievement['_id'])
    
    return jsonify({'achievements': achievements}), 200

@monitoring_bp.route("/monitoring/meeting-time/<engineer_id>", methods=["GET"])
def get_meeting_time(engineer_id):
    db = get_db()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get meeting tasks for today
    meeting_tasks = list(db.tasks.find({
        'engineerId': engineer_id,
        'createdAt': {'$gte': today},
        '$or': [
            {'title': {'$regex': 'meeting|zoom|call|sync|standup|review', '$options': 'i'}},
            {'description': {'$regex': 'meeting|zoom|call|sync|standup|review', '$options': 'i'}}
        ]
    }))
    
    # Calculate total meeting time
    total_meeting_time = sum((task.get('duration', 0) for task in meeting_tasks), 0)
    
    # Get idle time from monitoring sessions
    idle_time = sum(
        session.get('idleTime', 0)
        for session in db.monitoring_sessions.find({
            'engineerId': engineer_id,
            'startTime': {'$gte': today},
            'status': {'$in': ['stopped', 'idle']}
        })
    )
    
    return jsonify({
        'totalMeetingTime': total_meeting_time,
        'meetingCount': len(meeting_tasks),
        'idleTime': idle_time
    }), 200
