import pytest
from datetime import datetime, timedelta
from app.value_stream_service import calculate_cycle_time, calculate_lead_time

def test_calculate_cycle_time_empty():
    """Test cycle time calculation with empty events"""
    events = []
    cycle_time = calculate_cycle_time(events)
    assert cycle_time == 0

def test_calculate_cycle_time_single_event():
    """Test cycle time calculation with single event"""
    events = [{
        'eventType': 'code_started',
        'timestamp': datetime.utcnow()
    }]
    cycle_time = calculate_cycle_time(events)
    assert cycle_time == 0

def test_calculate_cycle_time_complete_flow():
    """Test cycle time calculation with complete event flow"""
    base_time = datetime.utcnow()
    events = [
        {
            'eventType': 'code_started',
            'timestamp': base_time
        },
        {
            'eventType': 'code_completed',
            'timestamp': base_time + timedelta(hours=2)
        },
        {
            'eventType': 'review_started',
            'timestamp': base_time + timedelta(hours=3)
        },
        {
            'eventType': 'review_completed',
            'timestamp': base_time + timedelta(hours=4)
        }
    ]
    cycle_time = calculate_cycle_time(events)
    assert cycle_time == 4  # 4 hours total

def test_calculate_cycle_time_missing_events():
    """Test cycle time calculation with missing events"""
    base_time = datetime.utcnow()
    events = [
        {
            'eventType': 'code_started',
            'timestamp': base_time
        },
        {
            'eventType': 'review_completed',
            'timestamp': base_time + timedelta(hours=4)
        }
    ]
    cycle_time = calculate_cycle_time(events)
    assert cycle_time == 4  # Should still calculate total time

def test_calculate_lead_time_empty():
    """Test lead time calculation with empty events"""
    events = []
    lead_time = calculate_lead_time(events)
    assert lead_time == 0

def test_calculate_lead_time_complete_flow():
    """Test lead time calculation with complete event flow"""
    base_time = datetime.utcnow()
    events = [
        {
            'eventType': 'task_created',
            'timestamp': base_time
        },
        {
            'eventType': 'code_started',
            'timestamp': base_time + timedelta(hours=1)
        },
        {
            'eventType': 'code_completed',
            'timestamp': base_time + timedelta(hours=3)
        },
        {
            'eventType': 'review_started',
            'timestamp': base_time + timedelta(hours=4)
        },
        {
            'eventType': 'review_completed',
            'timestamp': base_time + timedelta(hours=5)
        },
        {
            'eventType': 'deployed',
            'timestamp': base_time + timedelta(hours=6)
        }
    ]
    lead_time = calculate_lead_time(events)
    assert lead_time == 6  # 6 hours from creation to deployment

def test_calculate_lead_time_no_deployment():
    """Test lead time calculation without deployment event"""
    base_time = datetime.utcnow()
    events = [
        {
            'eventType': 'task_created',
            'timestamp': base_time
        },
        {
            'eventType': 'code_started',
            'timestamp': base_time + timedelta(hours=1)
        },
        {
            'eventType': 'code_completed',
            'timestamp': base_time + timedelta(hours=3)
        }
    ]
    lead_time = calculate_lead_time(events)
    assert lead_time == 0  # No deployment means no lead time

def test_calculate_lead_time_out_of_order():
    """Test lead time calculation with out-of-order events"""
    base_time = datetime.utcnow()
    events = [
        {
            'eventType': 'code_completed',
            'timestamp': base_time + timedelta(hours=3)
        },
        {
            'eventType': 'task_created',
            'timestamp': base_time
        },
        {
            'eventType': 'deployed',
            'timestamp': base_time + timedelta(hours=6)
        },
        {
            'eventType': 'code_started',
            'timestamp': base_time + timedelta(hours=1)
        }
    ]
    lead_time = calculate_lead_time(events)
    assert lead_time == 6  # Should handle out-of-order events

def test_calculate_lead_time_multiple_deployments():
    """Test lead time calculation with multiple deployment events"""
    base_time = datetime.utcnow()
    events = [
        {
            'eventType': 'task_created',
            'timestamp': base_time
        },
        {
            'eventType': 'deployed',
            'timestamp': base_time + timedelta(hours=4)
        },
        {
            'eventType': 'deployed',
            'timestamp': base_time + timedelta(hours=6)
        }
    ]
    lead_time = calculate_lead_time(events)
    assert lead_time == 4  # Should use first deployment
