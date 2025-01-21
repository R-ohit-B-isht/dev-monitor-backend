from flask import Blueprint, jsonify, request, current_app
from pymongo import MongoClient
from datetime import datetime
import requests
import json
from .utils.anonymization import hash_engineer_id, obfuscate_repository_name

notifications_bp = Blueprint("notifications", __name__)

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

def init_collections(db):
    """Initialize MongoDB collections and indexes for notifications"""
    if 'notification_settings' not in db.list_collection_names():
        db.create_collection('notification_settings')
    db.notification_settings.create_index([('engineerId', 1)], unique=True)
    
    if 'notification_history' not in db.list_collection_names():
        db.create_collection('notification_history')
    db.notification_history.create_index([('timestamp', -1)])
    db.notification_history.create_index([('engineerId', 1)])
    db.notification_history.create_index([('type', 1)])

def notify_slack(channel: str, message: str, blocks: list[dict] | None = None) -> bool:
    """Send notification to Slack channel"""
    try:
        webhook_url = current_app.config.get("SLACK_WEBHOOK_URL")
        if not webhook_url:
            print("Slack webhook URL not configured")
            return False

        payload = {
            "channel": channel,
            "text": message,
        }
        if blocks:
            payload["blocks"] = blocks

        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to send Slack notification: {str(e)}")
        return False

def notify_email(recipient: str, subject: str, body: str) -> bool:
    """Send email notification"""
    try:
        # Email configuration would go here
        # For now, just log the attempt
        print(f"Would send email to {recipient}: {subject}")
        return True
    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")
        return False

@notifications_bp.route("/notifications/settings/<engineer_id>", methods=["GET"])
def get_notification_settings(engineer_id):
    """Get notification settings for an engineer"""
    try:
        db = get_db()
        settings = db.notification_settings.find_one({'engineerId': hash_engineer_id(engineer_id)})
        
        if not settings:
            # Return default settings
            return jsonify({
                'email': True,
                'slack': True,
                'securityAlerts': True,
                'achievementAlerts': True,
                'focusTimeAlerts': True,
                'slackChannel': '#dev-productivity'
            }), 200
            
        settings.pop('_id', None)
        return jsonify(settings), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch notification settings: {str(e)}'}), 500

@notifications_bp.route("/notifications/settings/<engineer_id>", methods=["PUT"])
def update_notification_settings(engineer_id):
    """Update notification settings for an engineer"""
    try:
        db = get_db()
        settings = request.json
        
        result = db.notification_settings.update_one(
            {'engineerId': hash_engineer_id(engineer_id)},
            {'$set': settings},
            upsert=True
        )
        
        return jsonify({'message': 'Settings updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to update notification settings: {str(e)}'}), 500

@notifications_bp.route("/notifications/security-alert", methods=["POST"])
def send_security_alert():
    """Send notification for security alert"""
    try:
        data = request.json
        required_fields = ['repository', 'severity', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Get notification settings
        db = get_db()
        settings = db.notification_settings.find_one({'engineerId': hash_engineer_id(data.get('engineerId', 'current'))})
        
        if not settings:
            settings = {
                'email': True,
                'slack': True,
                'securityAlerts': True,
                'slackChannel': '#dev-productivity'
            }
            
        if not settings.get('securityAlerts', True):
            return jsonify({'message': 'Security alerts disabled'}), 200
            
        # Format message
        message = f"🚨 Security Alert ({data['severity'].upper()})\n"
        message += f"Repository: {obfuscate_repository_name(data['repository'])}\n"
        message += f"Description: {data['description']}"
        
        # Send notifications
        notifications_sent = []
        
        if settings.get('slack', True):
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 Security Alert - {data['severity'].upper()}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Repository:*\n{obfuscate_repository_name(data['repository'])}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity:*\n{data['severity'].upper()}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Description:*\n{data['description']}"
                    }
                }
            ]
            
            if notify_slack(settings.get('slackChannel', '#dev-productivity'), message, blocks):
                notifications_sent.append('slack')
                
        if settings.get('email', True):
            if notify_email(
                data.get('email', 'admin@example.com'),
                f"Security Alert: {data['severity'].upper()} - {obfuscate_repository_name(data['repository'])}",
                message
            ):
                notifications_sent.append('email')
                
        # Record notification
        db.notification_history.insert_one({
            'engineerId': hash_engineer_id(data.get('engineerId', 'current')),
            'type': 'security_alert',
            'severity': data['severity'],
            'repository': obfuscate_repository_name(data['repository']),
            'description': data['description'],
            'notifications_sent': notifications_sent,
            'timestamp': datetime.utcnow()
        })
        
        return jsonify({
            'message': 'Security alert sent',
            'notifications_sent': notifications_sent
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to send security alert: {str(e)}'}), 500

@notifications_bp.route("/notifications/achievement", methods=["POST"])
def send_achievement_notification():
    """Send notification for new achievement"""
    try:
        data = request.json
        required_fields = ['badge', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Get notification settings
        db = get_db()
        settings = db.notification_settings.find_one({'engineerId': hash_engineer_id(data.get('engineerId', 'current'))})
        
        if not settings:
            settings = {
                'email': True,
                'slack': True,
                'achievementAlerts': True,
                'slackChannel': '#dev-productivity'
            }
            
        if not settings.get('achievementAlerts', True):
            return jsonify({'message': 'Achievement alerts disabled'}), 200
            
        # Format message
        message = f"🏆 New Achievement Unlocked!\n"
        message += f"Badge: {data['badge']}\n"
        message += f"Description: {data['description']}"
        
        # Send notifications
        notifications_sent = []
        
        if settings.get('slack', True):
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🏆 Achievement Unlocked!"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Badge:*\n{data['badge']}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Description:*\n{data['description']}"
                    }
                }
            ]
            
            if notify_slack(settings.get('slackChannel', '#dev-productivity'), message, blocks):
                notifications_sent.append('slack')
                
        if settings.get('email', True):
            if notify_email(
                data.get('email', 'admin@example.com'),
                f"Achievement Unlocked: {data['badge']}",
                message
            ):
                notifications_sent.append('email')
                
        # Record notification
        db.notification_history.insert_one({
            'engineerId': hash_engineer_id(data.get('engineerId', 'current')),
            'type': 'achievement',
            'badge': data['badge'],
            'description': data['description'],
            'notifications_sent': notifications_sent,
            'timestamp': datetime.utcnow()
        })
        
        return jsonify({
            'message': 'Achievement notification sent',
            'notifications_sent': notifications_sent
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to send achievement notification: {str(e)}'}), 500
