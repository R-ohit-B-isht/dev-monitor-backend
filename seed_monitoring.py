from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/devin_tasks'))
db = client.get_database()

def seed_monitoring_data():
    # Clear existing data
    db.monitoring_sessions.delete_many({})
    db.activity_events.delete_many({})
    db.achievements.delete_many({})
    db.schedule_limits.delete_many({})

    # Create a monitoring session
    current_session = {
        'engineerId': 'current',
        'startTime': datetime.utcnow() - timedelta(hours=4),
        'status': 'running',
        'focusTime': 10800,  # 3 hours
        'idleTime': 1800,    # 30 minutes
        'productivityScore': 85.5
    }
    session_result = db.monitoring_sessions.insert_one(current_session)

    # Create activity events
    activities = [
        {
            'engineerId': 'current',
            'sessionId': str(session_result.inserted_id),
            'timestamp': datetime.utcnow() - timedelta(minutes=30),
            'eventType': 'keyboard',
            'metadata': {'keystrokes': 120}
        },
        {
            'engineerId': 'current',
            'sessionId': str(session_result.inserted_id),
            'timestamp': datetime.utcnow() - timedelta(minutes=20),
            'eventType': 'mouse',
            'metadata': {'clicks': 45}
        },
        {
            'engineerId': 'current',
            'sessionId': str(session_result.inserted_id),
            'timestamp': datetime.utcnow() - timedelta(minutes=10),
            'eventType': 'ide',
            'metadata': {'action': 'code_completion'}
        }
    ]
    db.activity_events.insert_many(activities)

    # Create achievements
    achievements = [
        {
            'engineerId': 'current',
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
            'engineerId': 'current',
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
        'engineerId': 'current',
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
