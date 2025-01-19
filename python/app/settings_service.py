from flask import Blueprint, request, jsonify
from datetime import datetime
from .monitoring_service import get_db
from bson.objectid import ObjectId

settings_bp = Blueprint("settings", __name__)

@settings_bp.route("/settings/<engineer_id>", methods=["GET"])
def get_settings(engineer_id):
    """Get all settings for an engineer"""
    db = get_db()
    settings = db.settings.find_one({'engineerId': engineer_id})
    if not settings:
        # Initialize default settings
        settings = {
            'engineerId': engineer_id,
            'schedule': {
                'dailyHourLimit': 8,
                'weeklyHourLimit': 40,
                'alertThreshold': 80
            },
            'notifications': {
                'email': True,
                'desktop': True,
                'slack': False,
                'scheduleAlerts': True,
                'achievementAlerts': True
            },
            'integrations': {
                'github': None,
                'jira': None,
                'linear': None
            },
            'display': {
                'theme': 'light',
                'compactView': False,
                'showAchievements': True,
                'defaultView': 'board'
            },
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        db.settings.insert_one(settings)
    
    settings['_id'] = str(settings['_id'])
    return jsonify(settings)

@settings_bp.route("/settings/<engineer_id>", methods=["PATCH"])
def update_settings(engineer_id):
    """Update settings for an engineer"""
    db = get_db()
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    # Validate notification settings
    if 'notifications' in data:
        if not isinstance(data['notifications'], dict):
            return jsonify({"error": "Invalid notifications format"}), 400
            
    # Validate integration settings
    if 'integrations' in data:
        if not isinstance(data['integrations'], dict):
            return jsonify({"error": "Invalid integrations format"}), 400
            
    # Validate display settings
    if 'display' in data:
        if not isinstance(data['display'], dict):
            return jsonify({"error": "Invalid display format"}), 400
        if 'theme' in data['display'] and data['display']['theme'] not in ['light', 'dark']:
            return jsonify({"error": "Invalid theme value"}), 400
    
    # Update settings
    update_data = {
        '$set': {
            **{k: v for k, v in data.items() if k != '_id'},
            'updatedAt': datetime.utcnow()
        }
    }
    
    result = db.settings.update_one(
        {'engineerId': engineer_id},
        update_data,
        upsert=True
    )
    
    if result.modified_count > 0 or result.upserted_id:
        return jsonify({"message": "Settings updated successfully"}), 200
    else:
        return jsonify({"message": "No changes made"}), 200

@settings_bp.route("/settings/<engineer_id>/notifications", methods=["PATCH"])
def update_notifications(engineer_id):
    """Update notification settings for an engineer"""
    db = get_db()
    data = request.json
    
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid notifications format"}), 400
        
    update_data = {
        '$set': {
            'notifications': data,
            'updatedAt': datetime.utcnow()
        }
    }
    
    result = db.settings.update_one(
        {'engineerId': engineer_id},
        update_data,
        upsert=True
    )
    
    if result.modified_count > 0 or result.upserted_id:
        return jsonify({"message": "Notification settings updated successfully"}), 200
    else:
        return jsonify({"message": "No changes made"}), 200

@settings_bp.route("/settings/<engineer_id>/integrations", methods=["PATCH"])
def update_integrations(engineer_id):
    """Update integration settings for an engineer"""
    db = get_db()
    data = request.json
    
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid integrations format"}), 400
        
    update_data = {
        '$set': {
            'integrations': data,
            'updatedAt': datetime.utcnow()
        }
    }
    
    result = db.settings.update_one(
        {'engineerId': engineer_id},
        update_data,
        upsert=True
    )
    
    if result.modified_count > 0 or result.upserted_id:
        return jsonify({"message": "Integration settings updated successfully"}), 200
    else:
        return jsonify({"message": "No changes made"}), 200



@settings_bp.route("/settings/<engineer_id>/schedule", methods=["GET"])
def get_schedule_limits(engineer_id):
    """Get schedule limits for an engineer"""
    db = get_db()
    settings = db.settings.find_one({'engineerId': engineer_id})
    if not settings or 'schedule' not in settings:
        return jsonify({
            'engineerId': engineer_id,
            'dailyHourLimit': 8,
            'weeklyHourLimit': 40,
            'alertThreshold': 80
        })
    schedule = settings['schedule']
    return jsonify({
        'engineerId': engineer_id,
        'dailyHourLimit': schedule['dailyHourLimit'],
        'weeklyHourLimit': schedule['weeklyHourLimit'],
        'alertThreshold': schedule.get('alertThreshold', 80)
    })

@settings_bp.route("/settings/<engineer_id>/schedule", methods=["PATCH"])
def update_schedule_limits(engineer_id):
    """Update schedule limits for an engineer"""
    db = get_db()
    data = request.json
    
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid schedule format"}), 400
        
    if 'dailyHourLimit' in data and not (1 <= data['dailyHourLimit'] <= 24):
        return jsonify({"error": "Daily hour limit must be between 1 and 24"}), 400
        
    if 'weeklyHourLimit' in data and not (1 <= data['weeklyHourLimit'] <= 168):
        return jsonify({"error": "Weekly hour limit must be between 1 and 168"}), 400
        
    update_data = {
        '$set': {
            'schedule': {
                'dailyHourLimit': data.get('dailyHourLimit', 8),
                'weeklyHourLimit': data.get('weeklyHourLimit', 40),
                'alertThreshold': data.get('alertThreshold', 80)
            },
            'updatedAt': datetime.utcnow()
        }
    }
    
    result = db.settings.update_one(
        {'engineerId': engineer_id},
        update_data,
        upsert=True
    )
    
    if result.modified_count > 0 or result.upserted_id:
        return jsonify({"message": "Schedule limits updated successfully"}), 200
    else:
        return jsonify({"message": "No changes made"}), 200

@settings_bp.route("/settings/<engineer_id>/display", methods=["PATCH"])
def update_display(engineer_id):
    """Update display settings for an engineer"""
    db = get_db()
    data = request.json
    
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid display settings format"}), 400
        
    if 'theme' in data and data['theme'] not in ['light', 'dark']:
        return jsonify({"error": "Invalid theme value"}), 400
        
    update_data = {
        '$set': {
            'display': data,
            'updatedAt': datetime.utcnow()
        }
    }
    
    result = db.settings.update_one(
        {'engineerId': engineer_id},
        update_data,
        upsert=True
    )
    
    if result.modified_count > 0 or result.upserted_id:
        return jsonify({"message": "Display settings updated successfully"}), 200
    else:
        return jsonify({"message": "No changes made"}), 200
