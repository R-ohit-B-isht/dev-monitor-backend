import pytest
from pymongo import MongoClient
from flask_cors import CORS
from app import create_app
from app.task_service import tasks_bp
from app.relationship_service import relationships_bp

@pytest.fixture
def app():
    app = create_app(register_blueprints=False)  # Don't register blueprints in create_app
    
    app.config.update({
        'TESTING': True,
        'MONGODB_URI': 'mongodb://localhost:27017',
        'MONGODB_DB': 'devin_tasks_test'
    })
    
    # Register blueprints here only
    from app.task_service import tasks_bp
    from app.relationship_service import relationships_bp
    app.register_blueprint(tasks_bp)
    app.register_blueprint(relationships_bp)
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    client = MongoClient(app.config['MONGODB_URI'])
    db = client[app.config['MONGODB_DB']]
    
    # Clear database before each test
    db.tasks.delete_many({})
    db.relationships.delete_many({})
    
    yield db
    
    # Clean up after test
    db.tasks.delete_many({})
    db.relationships.delete_many({})
    client.close()
