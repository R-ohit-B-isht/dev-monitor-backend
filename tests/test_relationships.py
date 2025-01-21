import pytest
from bson import ObjectId
from datetime import datetime
from app.relationship_service import create_relationship, get_relationships, delete_relationship
from app.task_service import update_task

def test_circular_dependency_detection(client, db):
    # Create test tasks
    task1 = db.tasks.insert_one({
        "title": "Task 1",
        "status": "To-Do",
        "integration": "github",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    })
    task2 = db.tasks.insert_one({
        "title": "Task 2",
        "status": "To-Do",
        "integration": "github",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    })
    task3 = db.tasks.insert_one({
        "title": "Task 3",
        "status": "To-Do",
        "integration": "github",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    })

    # Create a chain of blocking relationships
    response = client.post('/relationships', json={
        "sourceTaskId": str(task1.inserted_id),
        "targetTaskId": str(task2.inserted_id),
        "type": "blocks"
    })
    assert response.status_code == 201

    response = client.post('/relationships', json={
        "sourceTaskId": str(task2.inserted_id),
        "targetTaskId": str(task3.inserted_id),
        "type": "blocks"
    })
    assert response.status_code == 201

    # Try to create a circular dependency
    response = client.post('/relationships', json={
        "sourceTaskId": str(task3.inserted_id),
        "targetTaskId": str(task1.inserted_id),
        "type": "blocks"
    })
    assert response.status_code == 400
    assert "circular" in response.json["error"].lower()

def test_blocked_task_status_validation(client, db):
    # Create test tasks
    blocking_task = db.tasks.insert_one({
        "title": "Blocking Task",
        "status": "To-Do",
        "integration": "github",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    })
    blocked_task = db.tasks.insert_one({
        "title": "Blocked Task",
        "status": "To-Do",
        "integration": "github",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    })

    # Create blocking relationship
    response = client.post('/relationships', json={
        "sourceTaskId": str(blocking_task.inserted_id),
        "targetTaskId": str(blocked_task.inserted_id),
        "type": "blocks"
    })
    assert response.status_code == 201

    # Try to mark blocked task as Done
    response = client.patch(f'/tasks/{str(blocked_task.inserted_id)}', json={
        "status": "Done"
    })
    assert response.status_code == 400
    assert "blocked by" in response.json["error"].lower()

    # Mark blocking task as Done
    response = client.patch(f'/tasks/{str(blocking_task.inserted_id)}', json={
        "status": "Done"
    })
    assert response.status_code == 200

    # Now blocked task can be marked as Done
    response = client.patch(f'/tasks/{str(blocked_task.inserted_id)}', json={
        "status": "Done"
    })
    assert response.status_code == 200

def test_relationship_types(client, db):
    # Create test tasks
    task1 = db.tasks.insert_one({
        "title": "Task 1",
        "status": "To-Do",
        "integration": "github",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    })
    task2 = db.tasks.insert_one({
        "title": "Task 2",
        "status": "To-Do",
        "integration": "github",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    })

    # Test all valid relationship types
    valid_types = ["blocks", "blocked-by", "relates-to", "duplicates", "parent-of", "child-of"]
    for rel_type in valid_types:
        response = client.post('/relationships', json={
            "sourceTaskId": str(task1.inserted_id),
            "targetTaskId": str(task2.inserted_id),
            "type": rel_type
        })
        assert response.status_code == 201

        # Clean up for next iteration
        relationships = db.relationships.find({
            "sourceTaskId": str(task1.inserted_id),
            "targetTaskId": str(task2.inserted_id)
        })
        for rel in relationships:
            client.delete(f'/relationships/{str(rel["_id"])}')

    # Test invalid relationship type
    response = client.post('/relationships', json={
        "sourceTaskId": str(task1.inserted_id),
        "targetTaskId": str(task2.inserted_id),
        "type": "invalid-type"
    })
    assert response.status_code == 400
