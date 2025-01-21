import pytest
from datetime import datetime, timedelta
from app.monitoring_service import get_contribution_color
from app import create_app
import json

@pytest.fixture
def client():
    app = create_app(register_blueprints=True)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_contribution_color():
    assert get_contribution_color(0) == 0  # No contributions
    assert get_contribution_color(2) == 1  # Light
    assert get_contribution_color(6) == 2  # Medium
    assert get_contribution_color(10) == 3  # Dark
    assert get_contribution_color(15) == 4  # Very dark

def test_record_activity(client):
    # Test recording an activity with app focus
    response = client.post('/monitoring/activity', json={
        'engineerId': 'test-engineer',
        'sessionId': 'test-session',
        'eventType': 'keyboard',
        'appName': 'vscode',
        'metadata': {'key': 'value'}
    })
    assert response.status_code == 201
    assert b'Activity recorded' in response.data

def test_get_app_focus(client):
    # First record some test activities
    test_data = [
        {
            'engineerId': 'test-engineer',
            'sessionId': 'test-session',
            'eventType': 'keyboard',
            'appName': 'vscode',
            'metadata': {}
        },
        {
            'engineerId': 'test-engineer',
            'sessionId': 'test-session',
            'eventType': 'mouse',
            'appName': 'chrome',
            'metadata': {}
        }
    ]
    
    for activity in test_data:
        response = client.post('/monitoring/activity', json=activity)
        assert response.status_code == 201

    # Test getting app focus metrics
    response = client.get('/monitoring/app-focus/test-engineer')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'apps' in data
    assert 'totalFocusTime' in data
    assert 'timestamp' in data
    
    # Verify app data structure
    for app in data['apps']:
        assert 'appName' in app
        assert 'focusTime' in app
        assert 'eventCount' in app
        assert 'percentage' in app

def test_get_focus_metrics(client):
    response = client.get('/monitoring/focus-metrics/current')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'focusTimeSeconds' in data
    assert 'focusTimePercentage' in data
    assert 'totalActivities' in data
    assert 'focusActivities' in data
    assert 'focusActivityRatio' in data
    assert 'productivityScore' in data
    assert 'newBadges' in data

def test_start_time_tracking(client):
    response = client.post('/monitoring/start-time', json={
        'engineerId': 'test-engineer'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'sessionId' in data

def test_stop_time_tracking(client):
    # First start a session
    start_response = client.post('/monitoring/start-time', json={
        'engineerId': 'test-engineer'
    })
    session_id = json.loads(start_response.data)['sessionId']
    
    # Then stop it
    stop_response = client.post('/monitoring/stop-time', json={
        'sessionId': session_id
    })
    assert stop_response.status_code == 200
    data = json.loads(stop_response.data)
    assert 'duration' in data
