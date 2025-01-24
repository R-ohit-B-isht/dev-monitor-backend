import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from app.monitoring_service import get_contribution_color, get_contributions
from unittest.mock import MagicMock

def test_get_contribution_color():
    """Test contribution color intensity calculation"""
    assert get_contribution_color(0) == 0  # No tasks
    assert get_contribution_color(1) == 1  # 1-2 tasks
    assert get_contribution_color(2) == 1  # 1-2 tasks
    assert get_contribution_color(3) == 2  # 3-4 tasks
    assert get_contribution_color(4) == 2  # 3-4 tasks
    assert get_contribution_color(5) == 3  # 5-7 tasks
    assert get_contribution_color(7) == 3  # 5-7 tasks
    assert get_contribution_color(8) == 4  # 8-10 tasks
    assert get_contribution_color(10) == 4  # 8-10 tasks
    assert get_contribution_color(11) == 5  # 11+ tasks
    assert get_contribution_color(15) == 5  # 11+ tasks

@pytest.fixture
def mock_db():
    """Create a mock database with test tasks"""
    db = MagicMock()
    
    # Create test tasks with various dates and statuses
    now = datetime.utcnow()
    tasks = [
        # Today's tasks
        {
            '_id': ObjectId(),
            'status': 'Done',
            'updatedAt': now,
            'title': 'Task 1'
        },
        {
            '_id': ObjectId(),
            'status': 'Done',
            'updatedAt': now,
            'title': 'Task 2'
        },
        # Yesterday's tasks
        {
            '_id': ObjectId(),
            'status': 'Done',
            'updatedAt': now - timedelta(days=1),
            'title': 'Task 3'
        },
        # Task from last week
        {
            '_id': ObjectId(),
            'status': 'Done',
            'updatedAt': now - timedelta(days=7),
            'title': 'Task 4'
        },
        # Deleted task (should be filtered out)
        {
            '_id': ObjectId(),
            'status': 'Deleted',
            'updatedAt': now,
            'title': 'Task 5'
        },
        # In-Progress task (should be filtered out)
        {
            '_id': ObjectId(),
            'status': 'In-Progress',
            'updatedAt': now,
            'title': 'Task 6'
        }
    ]
    
    db.tasks.aggregate.return_value = tasks
    return db

def test_get_contributions(mock_db, monkeypatch):
    """Test contribution data aggregation and filtering"""
    
def test_month_boundaries(mock_db, monkeypatch):
    """Test contribution data handling across month boundaries"""
    def mock_get_db():
        return mock_db
    
    monkeypatch.setattr('app.monitoring_service.get_db', mock_get_db)
    
    # Create tasks spanning month boundary
    now = datetime(2024, 1, 31, 12, 0, 0)  # Last day of January
    tasks = [
        # January tasks
        {
            '_id': ObjectId(),
            'status': 'Done',
            'updatedAt': now,
            'title': 'End of January Task'
        },
        # February tasks
        {
            '_id': ObjectId(),
            'status': 'Done',
            'updatedAt': now + timedelta(days=1),  # February 1st
            'title': 'Start of February Task 1'
        },
        {
            '_id': ObjectId(),
            'status': 'Done',
            'updatedAt': now + timedelta(days=1),  # February 1st
            'title': 'Start of February Task 2'
        }
    ]
    
    mock_db.tasks.aggregate.return_value = tasks
    
    # Get contributions
    result = get_contributions('current')
    
    # Verify month structure
    assert len(result['months']) >= 2  # Should have both January and February
    
    # Find January and February data
    jan_data = next((m for m in result['months'] if m['name'] == 'January'), None)
    feb_data = next((m for m in result['months'] if m['name'] == 'February'), None)
    
    assert jan_data is not None, "January data missing"
    assert feb_data is not None, "February data missing"
    
    # Verify January contributions
    jan_31_contrib = next((c for c in jan_data['contributions'] if c['date'] == '2024-01-31'), None)
    assert jan_31_contrib is not None
    assert jan_31_contrib['count'] == 1
    assert jan_31_contrib['intensity'] == 1
    
    # Verify February contributions
    feb_1_contrib = next((c for c in feb_data['contributions'] if c['date'] == '2024-02-01'), None)
    assert feb_1_contrib is not None
    assert feb_1_contrib['count'] == 2
    assert feb_1_contrib['intensity'] == 1
    
    # Verify total contributions
    assert result['totalContributions'] == 3
    def mock_get_db():
        return mock_db
    
    monkeypatch.setattr('app.monitoring_service.get_db', mock_get_db)
    
    # Get contributions for the current user
    result = get_contributions('current')
    
    # Verify the response structure
    assert 'months' in result
    assert 'totalContributions' in result
    assert result['totalContributions'] == 4  # Total Done tasks
    
    # Find today's and yesterday's contributions
    now = datetime.utcnow()
    today_str = now.strftime('%Y-%m-%d')
    yesterday_str = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    last_week_str = (now - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Helper function to find contribution by date
    def find_contribution(date_str):
        for month in result['months']:
            for contrib in month['contributions']:
                if contrib['date'] == date_str:
                    return contrib
        return None
    
    # Check today's contributions
    today_contrib = find_contribution(today_str)
    assert today_contrib is not None
    assert today_contrib['count'] == 2  # 2 Done tasks today
    assert today_contrib['intensity'] == 1  # Intensity level 1 for 1-2 tasks
    
    # Check yesterday's contributions
    yesterday_contrib = find_contribution(yesterday_str)
    assert yesterday_contrib is not None
    assert yesterday_contrib['count'] == 1  # 1 Done task yesterday
    assert yesterday_contrib['intensity'] == 1  # Intensity level 1 for 1-2 tasks
    
    # Check last week's contributions
    last_week_contrib = find_contribution(last_week_str)
    assert last_week_contrib is not None
    assert last_week_contrib['count'] == 1  # 1 Done task last week
    assert last_week_contrib['intensity'] == 1  # Intensity level 1 for 1-2 tasks
    
    # Verify deleted and in-progress tasks are filtered out
    mock_db.tasks.aggregate.assert_called_once()
    pipeline = mock_db.tasks.aggregate.call_args[0][0]
    match_stage = next(stage for stage in pipeline if '$match' in stage)
    assert match_stage['$match']['status'] == 'Done'
    assert match_stage['$match']['$or'] == [
        {'status': {'$ne': 'Deleted'}},
        {'isDeleted': {'$ne': True}},
        {'isDeleted': {'$exists': False}}
    ]
