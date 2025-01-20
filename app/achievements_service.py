from flask import Blueprint, jsonify, request, current_app
from pymongo import MongoClient
from datetime import datetime, timedelta
from .utils.anonymization import hash_engineer_id
from .notifications_service import notify_slack, notify_email

achievements_bp = Blueprint("achievements", __name__)

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

# Achievement definitions
ACHIEVEMENTS = {
    'secure_developer': {
        'name': 'Secure Developer',
        'description': 'No security warnings in code scanning',
        'icon': '🛡️',
        'type': 'security'
    },
    'security_champion': {
        'name': 'Security Champion',
        'description': 'Fixed 10 security vulnerabilities',
        'icon': '🔒',
        'type': 'security'
    },
    'merge_master': {
        'name': 'Merge Master',
        'description': '5 successful merges in a week',
        'icon': '🔄',
        'type': 'collaboration'
    },
    'rapid_resolver': {
        'name': 'Rapid Resolver',
        'description': 'Fixed a critical security issue within 24 hours',
        'icon': '⚡',
        'type': 'security'
    }
}

def grant_achievement(db, engineer_id, achievement_id, metadata=None):
    """Grant an achievement to an engineer"""
    if achievement_id not in ACHIEVEMENTS:
        return False
        
    achievement = ACHIEVEMENTS[achievement_id]
    hashed_id = hash_engineer_id(engineer_id)
    
    # Check if already earned today
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    existing = db.achievements.find_one({
        'engineerId': hashed_id,
        'badge': achievement['name'],
        'earnedAt': {'$gte': today}
    })
    
    if existing:
        return False
        
    # Record achievement
    achievement_doc = {
        'engineerId': hashed_id,
        'badge': achievement['name'],
        'description': achievement['description'],
        'icon': achievement['icon'],
        'type': achievement['type'],
        'earnedAt': datetime.utcnow(),
        'metadata': metadata or {}
    }
    
    db.achievements.insert_one(achievement_doc)
    
    # Send notifications
    try:
        message = f"{achievement['icon']} Achievement Unlocked: {achievement['name']}\n{achievement['description']}"
        notify_slack('#dev-productivity', message)
        notify_email('admin@example.com', 'New Achievement Unlocked', message)
    except Exception as e:
        print(f"Failed to send achievement notification: {str(e)}")
        
    return True

def check_security_achievements(db, engineer_id):
    """Check and grant security-related achievements"""
    hashed_id = hash_engineer_id(engineer_id)
    
    # Check for zero security warnings
    alerts = db.security_alerts.count_documents({
        'engineerId': hashed_id,
        'state': 'open'
    })
    
    if alerts == 0:
        grant_achievement(db, engineer_id, 'secure_developer')
    
    # Check for fixed vulnerabilities
    fixed_count = db.security_alerts.count_documents({
        'engineerId': hashed_id,
        'state': 'fixed',
        'updated_at': {'$gte': datetime.utcnow() - timedelta(days=30)}
    })
    
    if fixed_count >= 10:
        grant_achievement(db, engineer_id, 'security_champion', {
            'fixed_count': fixed_count
        })
    
    # Check for rapid security fixes
    rapid_fixes = db.security_alerts.find({
        'engineerId': hashed_id,
        'state': 'fixed',
        'severity': 'critical'
    })
    
    for fix in rapid_fixes:
        if fix.get('updated_at') and fix.get('created_at'):
            fix_time = datetime.fromisoformat(fix['updated_at']) - datetime.fromisoformat(fix['created_at'])
            if fix_time.total_seconds() <= 24 * 3600:  # 24 hours
                grant_achievement(db, engineer_id, 'rapid_resolver', {
                    'alert_id': str(fix['_id']),
                    'fix_time_hours': fix_time.total_seconds() / 3600
                })

def check_merge_achievements(db, engineer_id):
    """Check and grant merge-related achievements"""
    hashed_id = hash_engineer_id(engineer_id)
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Count successful merges in the last week
    merge_count = db.git_events.count_documents({
        'engineerId': hashed_id,
        'eventType': 'merge',
        'status': 'success',
        'timestamp': {'$gte': week_ago}
    })
    
    if merge_count >= 5:
        grant_achievement(db, engineer_id, 'merge_master', {
            'merge_count': merge_count,
            'timeframe': '7d'
        })

@achievements_bp.route("/achievements/check/<engineer_id>", methods=["POST"])
def check_achievements(engineer_id):
    """Check all achievement types for an engineer"""
    try:
        db = get_db()
        
        check_security_achievements(db, engineer_id)
        check_merge_achievements(db, engineer_id)
        
        return jsonify({'message': 'Achievements checked successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to check achievements: {str(e)}'}), 500

@achievements_bp.route("/achievements/<engineer_id>", methods=["GET"])
def get_achievements(engineer_id):
    """Get all achievements for an engineer"""
    try:
        db = get_db()
        hashed_id = hash_engineer_id(engineer_id)
        
        achievements = list(db.achievements.find({
            'engineerId': hashed_id
        }).sort('earnedAt', -1))
        
        # Convert ObjectId to string for JSON serialization
        for achievement in achievements:
            achievement['_id'] = str(achievement['_id'])
            
        return jsonify({
            'achievements': achievements,
            'total': len(achievements)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch achievements: {str(e)}'}), 500
