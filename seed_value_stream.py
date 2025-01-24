from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
from app.utils.anonymization import hash_engineer_id

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/devin_tasks'))
db = client.get_database()

# Hash the engineer ID once
ENGINEER_ID = hash_engineer_id('current')

def seed_value_stream_data():
    # Clear existing data
    db.value_stream_events.delete_many({})
    db.tasks.delete_many({})  # Clear existing tasks
    
    # Create some test tasks
    tasks = [
        {
            'title': 'Implement AI Metrics',
            'status': 'Done',
            'integration': 'github',
            'engineerId': ENGINEER_ID,
            'createdAt': datetime.utcnow() - timedelta(days=2),
            'updatedAt': datetime.utcnow() - timedelta(hours=4)
        },
        {
            'title': 'Add Security Dashboard',
            'status': 'In-Progress',
            'integration': 'github',
            'engineerId': ENGINEER_ID,
            'createdAt': datetime.utcnow() - timedelta(days=1),
            'updatedAt': datetime.utcnow() - timedelta(hours=2)
        }
    ]
    
    task_ids = []
    for task in tasks:
        result = db.tasks.insert_one(task)
        task_ids.append(result.inserted_id)
    
    # Create value stream events for the first task
    events_task1 = [
        {
            'engineerId': ENGINEER_ID,
            'taskId': task_ids[0],
            'eventType': 'code_started',
            'createdAt': datetime.utcnow() - timedelta(days=2, hours=22),
            'metadata': {
                'branch': 'feature/ai-metrics',
                'linesChanged': 150
            }
        },
        {
            'engineerId': ENGINEER_ID,
            'taskId': task_ids[0],
            'eventType': 'code_completed',
            'createdAt': datetime.utcnow() - timedelta(days=2, hours=18),
            'metadata': {
                'commits': 3,
                'filesChanged': 5
            }
        },
        {
            'engineerId': ENGINEER_ID,
            'taskId': task_ids[0],
            'eventType': 'review_started',
            'createdAt': datetime.utcnow() - timedelta(days=2, hours=17),
            'metadata': {
                'reviewers': 2
            }
        },
        {
            'engineerId': ENGINEER_ID,
            'taskId': task_ids[0],
            'eventType': 'review_completed',
            'createdAt': datetime.utcnow() - timedelta(days=2, hours=15),
            'metadata': {
                'comments': 5,
                'approved': True
            }
        },
        {
            'engineerId': ENGINEER_ID,
            'taskId': task_ids[0],
            'eventType': 'merged',
            'createdAt': datetime.utcnow() - timedelta(days=2, hours=14),
            'metadata': {
                'mergeCommit': 'abc123'
            }
        },
        {
            'engineerId': ENGINEER_ID,
            'taskId': task_ids[0],
            'eventType': 'deployed',
            'createdAt': datetime.utcnow() - timedelta(days=2, hours=13),
            'metadata': {
                'environment': 'production'
            }
        }
    ]
    
    # Create value stream events for the second task (in progress)
    events_task2 = [
        {
            'engineerId': ENGINEER_ID,
            'taskId': task_ids[1],
            'eventType': 'code_started',
            'createdAt': datetime.utcnow() - timedelta(days=1, hours=10),
            'metadata': {
                'branch': 'feature/security-dashboard',
                'linesChanged': 80
            }
        },
        {
            'engineerId': ENGINEER_ID,
            'taskId': task_ids[1],
            'eventType': 'code_completed',
            'createdAt': datetime.utcnow() - timedelta(days=1, hours=6),
            'metadata': {
                'commits': 2,
                'filesChanged': 3
            }
        },
        {
            'engineerId': ENGINEER_ID,
            'taskId': task_ids[1],
            'eventType': 'review_started',
            'createdAt': datetime.utcnow() - timedelta(days=1, hours=5),
            'metadata': {
                'reviewers': 1
            }
        }
    ]
    
    # Insert all events
    all_events = events_task1 + events_task2
    db.value_stream_events.insert_many(all_events)
    
    print("Value stream data seeded successfully!")
    print(f"Created:")
    print(f"- {len(tasks)} tasks")
    print(f"- {len(all_events)} value stream events")

if __name__ == "__main__":
    seed_value_stream_data()
