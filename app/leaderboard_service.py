from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from .monitoring_service import get_db

leaderboard_bp = Blueprint("leaderboard", __name__)

@leaderboard_bp.route("/leaderboard/daily", methods=["GET"])
def get_daily_leaderboard():
    db = get_db()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    pipeline = [
        {
            '$match': {
                'startTime': {'$gte': today},
                'status': 'stopped'
            }
        },
        {
            '$group': {
                '_id': '$engineerId',
                'codingTime': {'$sum': '$focusTime'},
                'focusScore': {'$avg': '$productivityScore'},
                'achievements': {'$addToSet': '$achievements'}
            }
        },
        {'$sort': {'codingTime': -1}}
    ]
    
    results = list(db.monitoring_sessions.aggregate(pipeline))
    return jsonify(results), 200

@leaderboard_bp.route("/leaderboard/weekly", methods=["GET"])
def get_weekly_leaderboard():
    db = get_db()
    week_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=datetime.utcnow().weekday())
    
    pipeline = [
        {
            '$match': {
                'startTime': {'$gte': week_start},
                'status': 'stopped'
            }
        },
        {
            '$group': {
                '_id': '$engineerId',
                'codingTime': {'$sum': '$focusTime'},
                'focusScore': {'$avg': '$productivityScore'},
                'achievements': {'$addToSet': '$achievements'}
            }
        },
        {'$sort': {'codingTime': -1}}
    ]
    
    results = list(db.monitoring_sessions.aggregate(pipeline))
    return jsonify(results), 200
