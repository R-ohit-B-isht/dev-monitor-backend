import pytest
from app import create_app
from pymongo import MongoClient

@pytest.fixture
def app():
    """Create and configure a test Flask app instance"""
    app = create_app(register_blueprints=True)
    app.config.update({
        'TESTING': True,
        'MONGODB_URI': 'mongodb://localhost:27017',
        'MONGODB_DB': 'devin_tasks_test'
    })
    return app

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def db(app):
    """Create a test database connection"""
    with app.app_context():
        client = MongoClient(app.config['MONGODB_URI'])
        db = client[app.config['MONGODB_DB']]
        yield db
        # Clean up after tests
        client.drop_database(app.config['MONGODB_DB'])
