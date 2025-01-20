from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from .monitoring_service import get_db

schedule_bp = Blueprint("schedule", __name__)

def start_monitoring_thread(app):
    """Start background thread for monitoring schedule limits"""
    # This would typically start a background thread
    # For now, we'll just initialize the collection
    with app.app_context():
        db = get_db()
        if 'schedule_limits' not in db.list_collection_names():
            db.schedule_limits.insert_one({
                'engineerId': 'current',
                'dailyHourLimit': 8,
                'weeklyHourLimit': 40,
                'alertThreshold': 80
            })

@schedule_bp.route("/monitoring/schedule-limits/<engineer_id>", methods=["GET"])
def get_schedule_limits(engineer_id):
    db = get_db()
    limits = db.schedule_limits.find_one({'engineerId': engineer_id})
    if not limits:
        return jsonify({'error': 'Schedule limits not found'}), 404
    limits['_id'] = str(limits['_id'])
    return jsonify(limits)

@schedule_bp.route("/monitoring/schedule-limits", methods=["POST"])
def set_schedule_limits():
    db = get_db()
    data = request.json
    
    if not all(k in data for k in ['engineerId', 'dailyHourLimit', 'weeklyHourLimit']):
        return jsonify({'error': 'Missing required fields'}), 400
        
    result = db.schedule_limits.update_one(
        {'engineerId': data['engineerId']},
        {'$set': {
            'dailyHourLimit': data['dailyHourLimit'],
            'weeklyHourLimit': data['weeklyHourLimit'],
            'alertThreshold': data.get('alertThreshold', 80),
            'updatedAt': datetime.utcnow()
        }},
        upsert=True
    )
    
    return jsonify({'message': 'Schedule limits updated'}), 200
