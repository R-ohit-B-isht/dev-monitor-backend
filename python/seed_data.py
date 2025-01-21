from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/devin_tasks'))
db = client.get_database()

def seed_tasks():
    # Clear existing data
    db.tasks.delete_many({})
    db.relationships.delete_many({})

    # Sample tasks with different integrations and statuses
    tasks = [
        {
            "title": "Setup CI/CD Pipeline",
            "description": "Configure GitHub Actions for automated testing and deployment",
            "status": "In-Progress",
            "integration": "github",
            "createdAt": datetime.utcnow() - timedelta(days=5),
            "updatedAt": datetime.utcnow() - timedelta(days=2)
        },
        {
            "title": "Update User Authentication",
            "description": "Implement OAuth2 and refresh token functionality",
            "status": "To-Do",
            "integration": "github",
            "createdAt": datetime.utcnow() - timedelta(days=3),
            "updatedAt": datetime.utcnow() - timedelta(days=3)
        },
        {
            "title": "Bug: Login Page Crash",
            "description": "Fix crash when clicking login with empty credentials",
            "status": "Done",
            "integration": "jira",
            "createdAt": datetime.utcnow() - timedelta(days=7),
            "updatedAt": datetime.utcnow() - timedelta(hours=12)
        },
        {
            "title": "Design System Implementation",
            "description": "Create reusable component library based on new design system",
            "status": "In-Progress",
            "integration": "linear",
            "createdAt": datetime.utcnow() - timedelta(days=10),
            "updatedAt": datetime.utcnow() - timedelta(days=1)
        },
        {
            "title": "API Documentation",
            "description": "Update API documentation with new endpoints",
            "status": "To-Do",
            "integration": "jira",
            "createdAt": datetime.utcnow() - timedelta(days=2),
            "updatedAt": datetime.utcnow() - timedelta(days=2)
        }
    ]

    # Insert tasks and store their IDs
    task_ids = {}
    for task in tasks:
        result = db.tasks.insert_one(task)
        task_ids[task["title"]] = str(result.inserted_id)

    # Create relationships between tasks
    relationships = [
        {
            "sourceTaskId": task_ids["Update User Authentication"],
            "targetTaskId": task_ids["Setup CI/CD Pipeline"],
            "type": "blocks",
            "createdAt": datetime.utcnow() - timedelta(days=3),
            "updatedAt": datetime.utcnow() - timedelta(days=3)
        },
        {
            "sourceTaskId": task_ids["API Documentation"],
            "targetTaskId": task_ids["Design System Implementation"],
            "type": "relates-to",
            "createdAt": datetime.utcnow() - timedelta(days=2),
            "updatedAt": datetime.utcnow() - timedelta(days=2)
        }
    ]

    # Insert relationships
    if relationships:
        db.relationships.insert_many(relationships)

    print("Database seeded successfully!")
    print(f"Created {len(tasks)} tasks and {len(relationships)} relationships")

if __name__ == "__main__":
    seed_tasks()
