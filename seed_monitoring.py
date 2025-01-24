from pymongo import MongoClient
from datetime import datetime, timedelta
import os
import sys
from dotenv import load_dotenv

# Add app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils.anonymization import hash_engineer_id

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/devin_tasks'))
db = client.get_database()

# Hash the engineer ID once
ENGINEER_ID = hash_engineer_id('current')

def seed_monitoring_data():
    # Clear existing data
    db.monitoring_sessions.delete_many({})
    db.activity_events.delete_many({})
    db.achievements.delete_many({})
    db.schedule_limits.delete_many({})

    # Create a monitoring session
    current_session = {
        'engineerId': ENGINEER_ID,
        'startTime': datetime.utcnow() - timedelta(hours=4),
        'status': 'running',
        'focusTime': 10800,  # 3 hours
        'productivityScore': 85.5
    }
    session_result = db.monitoring_sessions.insert_one(current_session)

    # Create activity events
    activities = [
        {
            'engineerId': ENGINEER_ID,
            'sessionId': str(session_result.inserted_id),
            'timestamp': datetime.utcnow() - timedelta(minutes=30),
            'eventType': 'keyboard',
            'metadata': {
                'keystrokes': 120,
                'linesOfCodeModified': 25,
                'filesChanged': 3,
                'testCoverage': 78.5,
                'responseTime': 150
            }
        },
        {
            'engineerId': ENGINEER_ID,
            'sessionId': str(session_result.inserted_id),
            'timestamp': datetime.utcnow() - timedelta(minutes=20),
            'eventType': 'mouse',
            'metadata': {
                'clicks': 45,
                'linesOfCodeModified': 15,
                'filesChanged': 2,
                'testCoverage': 82.3,
                'responseTime': 120
            }
        },
        {
            'engineerId': ENGINEER_ID,
            'sessionId': str(session_result.inserted_id),
            'timestamp': datetime.utcnow() - timedelta(minutes=10),
            'eventType': 'ide',
            'metadata': {
                'action': 'code_completion',
                'linesOfCodeModified': 35,
                'filesChanged': 4,
                'testCoverage': 75.8,
                'responseTime': 180
            }
        }
    ]
    db.activity_events.insert_many(activities)

    # Create achievements
    achievements = [
        {
            'engineerId': ENGINEER_ID,
            'badge': 'Focus Master',
            'earnedAt': datetime.utcnow() - timedelta(hours=2),
            'metadata': {
                'sessionId': str(session_result.inserted_id),
                'productivityScore': 92,
                'focusTime': 7200,
                'totalActivities': 150
            }
        },
        {
            'engineerId': ENGINEER_ID,
            'badge': 'Code Warrior',
            'earnedAt': datetime.utcnow() - timedelta(hours=1),
            'metadata': {
                'sessionId': str(session_result.inserted_id),
                'productivityScore': 88,
                'focusTime': 5400,
                'totalActivities': 120
            }
        }
    ]
    db.achievements.insert_many(achievements)

    # Create schedule limits
    schedule_limit = {
        'engineerId': ENGINEER_ID,
        'dailyHourLimit': 8,
        'weeklyHourLimit': 40,
        'alertThreshold': 80,
        'updatedAt': datetime.utcnow()
    }
    db.schedule_limits.insert_one(schedule_limit)

    print("Monitoring data seeded successfully!")
    print(f"Created:")
    print(f"- 1 monitoring session")
    print(f"- {len(activities)} activity events")
    print(f"- {len(achievements)} achievements")
    print(f"- 1 schedule limit")

if __name__ == "__main__":
    seed_monitoring_data()
