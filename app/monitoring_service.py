from flask import Blueprint, jsonify, request, current_app
from pymongo import MongoClient
from datetime import datetime, timedelta
import json
import threading
import time
from .utils.anonymization import hash_engineer_id, generate_anonymous_id
from calendar import monthrange
from .notifications_service import notify_slack, notify_email

monitoring_bp = Blueprint("monitoring", __name__)

def read_cpu_stats():
    """Read CPU statistics from /proc/stat"""
    try:
        with open('/proc/stat', 'r') as f:
            cpu_stats = f.readline().split()
            user = float(cpu_stats[1])
            nice = float(cpu_stats[2])
            system = float(cpu_stats[3])
            idle = float(cpu_stats[4])
            total = user + nice + system + idle
            return {
                'usage_percent': ((total - idle) / total) * 100,
                'user': user,
                'system': system,
                'idle': idle
            }
    except Exception as e:
        print(f"Error reading CPU stats: {str(e)}")
        return None

def read_memory_stats():
    """Read memory statistics from /proc/meminfo"""
    try:
        memory_stats = {}
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if ':' in line:
                    key, value = line.split(':')
                    value = value.strip()
                    if 'kB' in value:
                        value = int(value.replace('kB', '').strip()) * 1024
                    memory_stats[key.strip()] = value
        
        total = int(memory_stats.get('MemTotal', 0))
        available = int(memory_stats.get('MemAvailable', 0))
        used = total - available
        
        return {
            'total': total,
            'available': available,
            'used': used,
            'usage_percent': (used / total) * 100 if total > 0 else 0
        }
    except Exception as e:
        print(f"Error reading memory stats: {str(e)}")
        return None

def monitor_system_performance(app_context):
    """Background thread to monitor system performance"""
    with app_context:
        db = get_db()
        last_cpu_stats = None
        
        while True:
            try:
                # Get current stats
                cpu_stats = read_cpu_stats()
                memory_stats = read_memory_stats()
                
                if cpu_stats and memory_stats:
                    # Determine severity
                    severity = 'info'
                    if cpu_stats['usage_percent'] > 90 or memory_stats['usage_percent'] > 90:
                        severity = 'critical'
                    elif cpu_stats['usage_percent'] > 75 or memory_stats['usage_percent'] > 75:
                        severity = 'warning'
                    elif cpu_stats['usage_percent'] > 50 or memory_stats['usage_percent'] > 50:
                        severity = 'moderate'
                    
                    # Log event if resource usage is moderate or higher
                    if severity != 'info':
                        event = {
                            'timestamp': datetime.utcnow(),
                            'type': 'resource_usage',
                            'severity': severity,
                            'metrics': {
                                'cpu': cpu_stats,
                                'memory': memory_stats
                            }
                        }
                        db.performance_events.insert_one(event)
                        
                        # Send notification for critical events
                        if severity == 'critical':
                            try:
                                message = f"🚨 Critical Resource Usage Alert:\nCPU: {cpu_stats['usage_percent']:.1f}%\nMemory: {memory_stats['usage_percent']:.1f}%"
                                notify_slack('#monitoring-alerts', message)
                            except Exception as e:
                                print(f"Failed to send notification: {str(e)}")
                
                # Sleep for monitoring interval
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Error in performance monitoring: {str(e)}")
                time.sleep(60)  # Wait before retrying

def start_performance_monitoring(app):
    """Start the performance monitoring thread"""
    monitor_thread = threading.Thread(
        target=monitor_system_performance,
        args=(app.app_context(),),
        daemon=True
    )
    monitor_thread.start()

def get_contribution_color(count):
    """Return color intensity based on contribution count using GitHub-style thresholds"""
    if count == 0:
        return 0  # No contributions
    elif count <= 4:
        return 1  # Light
    elif count <= 8:
        return 2  # Medium
    elif count <= 12:
        return 3  # Dark
    else:
        return 4  # Very dark

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

@monitoring_bp.route("/monitoring/performance", methods=["GET"])
def get_performance_metrics():
    """Get recent performance metrics"""
    try:
        db = get_db()
        days = int(request.args.get('days', '1'))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get recent performance events
        events = list(db.performance_events.find({
            'timestamp': {'$gte': start_date}
        }).sort('timestamp', -1))
        
        # Convert ObjectId to string for JSON serialization
        for event in events:
            event['_id'] = str(event['_id'])
            
        # Calculate summary statistics
        total_events = len(events)
        critical_events = sum(1 for e in events if e['severity'] == 'critical')
        warning_events = sum(1 for e in events if e['severity'] == 'warning')
        
        return jsonify({
            'events': events,
            'summary': {
                'total': total_events,
                'critical': critical_events,
                'warning': warning_events
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch performance metrics: {str(e)}'}), 500

@monitoring_bp.route("/monitoring/focus-metrics/current", methods=["GET"])
def get_focus_metrics():
    db = get_db()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get today's monitoring sessions
    hashed_id = hash_engineer_id('current')
    sessions = list(db.monitoring_sessions.find({
        'engineerId': hashed_id,
        'startTime': {'$gte': today},
        'status': {'$in': ['stopped', 'idle']}
    }))
    
    total_focus_time = sum(s.get('focusTime', 0) for s in sessions)
    total_time = sum((s.get('focusTime', 0) + s.get('idleTime', 0)) for s in sessions)
    focus_percentage = (total_focus_time / total_time * 100) if total_time > 0 else 0
    
    # Get activity counts
    activities = list(db.activity_events.find({
        'engineerId': hashed_id,
        'timestamp': {'$gte': today}
    }))
    
    focus_activities = len([a for a in activities if a['eventType'] in ['keyboard', 'mouse', 'ide']])
    
    # Calculate productivity score (60% focus time, 40% activity type)
    productivity_score = (0.6 * focus_percentage) + (0.4 * (focus_activities / len(activities) * 100)) if activities else 0
    
    # Get new badges earned today
    new_badges = [a['badge'] for a in db.achievements.find({
        'engineerId': hashed_id,
        'earnedAt': {'$gte': today}
    })]
    
    # Send notifications for new achievements
    for badge in new_badges:
        try:
            notify_slack('#dev-productivity', f"🏆 Achievement Unlocked: {badge}")
            notify_email('admin@example.com', 'New Achievement Unlocked', f"You've earned the {badge} badge!")
        except Exception as e:
            print(f"Failed to send achievement notification: {str(e)}")
    
    return jsonify({
        'focusTimeSeconds': total_focus_time,
        'focusTimePercentage': focus_percentage,
        'totalActivities': len(activities),
        'focusActivities': focus_activities,
        'focusActivityRatio': focus_activities / len(activities) if activities else 0,
        'productivityScore': productivity_score,
        'newBadges': new_badges
    }), 200

@monitoring_bp.route("/monitoring/start-time", methods=["POST"])
def start_time_tracking():
    db = get_db()
    data = request.json
    
    session = {
        'engineerId': data['engineerId'],
        'startTime': datetime.utcnow(),
        'status': 'running',
        'focusTime': 0,
        'idleTime': 0
    }
    
    result = db.monitoring_sessions.insert_one(session)
    return jsonify({'sessionId': str(result.inserted_id)}), 201

@monitoring_bp.route("/monitoring/stop-time", methods=["POST"])
def stop_time_tracking():
    db = get_db()
    data = request.json
    
    session = db.monitoring_sessions.find_one_and_update(
        {'_id': data['sessionId'], 'status': 'running'},
        {
            '$set': {
                'status': 'stopped',
                'endTime': datetime.utcnow()
            }
        }
    )
    
    if not session:
        return jsonify({'error': 'Session not found or already stopped'}), 404
        
    duration = (datetime.utcnow() - session['startTime']).total_seconds()
    return jsonify({'duration': duration}), 200

@monitoring_bp.route("/monitoring/activity", methods=["POST"])
def record_activity():
    db = get_db()
    data = request.json
    
    event = {
        'engineerId': data['engineerId'],
        'sessionId': data['sessionId'],
        'timestamp': datetime.utcnow(),
        'eventType': data['eventType'],
        'metadata': data.get('metadata', {})
    }
    
    db.activity_events.insert_one(event)
    return jsonify({'message': 'Activity recorded'}), 201

@monitoring_bp.route("/monitoring/achievements/current", methods=["GET"])
def get_achievements():
    db = get_db()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    achievements = list(db.achievements.find({
        'engineerId': 'current',
        'earnedAt': {'$gte': today}
    }))
    
    # Convert ObjectId to string for JSON serialization
    for achievement in achievements:
        achievement['_id'] = str(achievement['_id'])
    
    return jsonify({'achievements': achievements}), 200

@monitoring_bp.route("/monitoring/contributions/<engineer_id>", methods=["GET"])
def get_contributions(engineer_id):
    """Get contribution data for the last year"""
    db = get_db()
    end_date = datetime.utcnow().replace(hour=23, minute=59, second=59)
    start_date = (end_date - timedelta(days=364)).replace(hour=0, minute=0, second=0)
    
    # For testing: Generate some sample contribution data with realistic patterns
    test_data = []
    current_date = start_date
    
    # Pre-calculate month boundaries
    month_days = {}
    temp_date = start_date
    while temp_date <= end_date:
        month_key = temp_date.strftime("%Y-%m")
        if month_key not in month_days:
            _, days_in_month = monthrange(temp_date.year, temp_date.month)
            month_days[month_key] = days_in_month
        temp_date += timedelta(days=1)
    
    while current_date <= end_date:
        # Generate contribution counts with realistic patterns
        weekday = current_date.weekday()
        week_of_year = current_date.isocalendar()[1]
        
        # Base contribution pattern
        if weekday in [5, 6]:  # Weekends
            base_count = 0
        else:
            # More contributions mid-week
            base_count = 4 + int(6 * (1 - abs(weekday - 2) / 4))
        
        # Add weekly pattern variations
        if week_of_year % 4 == 0:  # High activity weeks
            count = base_count + 6
        elif week_of_year % 4 == 1:  # Medium-high activity weeks
            count = base_count + 3
        elif week_of_year % 4 == 2:  # Medium-low activity weeks
            count = max(0, base_count - 1)
        else:  # Low activity weeks
            count = max(0, base_count - 3)
            
        # Add some randomness
        import random
        count = max(0, int(count * (0.8 + random.random() * 0.4)))
        
        test_data.append({
            'date': current_date.strftime("%Y-%m-%d"),
            'count': count,
            'intensity': get_contribution_color(count)
        })
        current_date += timedelta(days=1)
    
    # Group by month for easier rendering
    months = {}
    total_contributions = 0
    
    # Initialize all months with empty contributions
    temp_date = start_date
    while temp_date <= end_date:
        month_key = temp_date.strftime("%Y-%m")
        if month_key not in months:
            days_in_month = month_days[month_key]
            month_start = temp_date.replace(day=1)
            
            # Initialize contributions with proper dates
            contributions = []
            for day in range(days_in_month):
                day_date = month_start + timedelta(days=day)
                contributions.append({
                    'date': day_date.strftime("%Y-%m-%d"),
                    'count': 0,
                    'intensity': 0
                })
            
            months[month_key] = {
                'year': temp_date.year,
                'month': temp_date.month,
                'name': temp_date.strftime("%B"),
                'days': days_in_month,
                'contributions': contributions
            }
        temp_date += timedelta(days=1)
    
    # Fill in actual contributions
    for contrib in test_data:
        date = datetime.strptime(contrib['date'], "%Y-%m-%d")
        month_key = date.strftime("%Y-%m")
        day_index = date.day - 1  # Convert to 0-based index
        months[month_key]['contributions'][day_index] = contrib
        total_contributions += contrib['count']
    
    return jsonify({
        'months': list(months.values()),
        'totalContributions': total_contributions
    }), 200

@monitoring_bp.route("/monitoring/meeting-time/<engineer_id>", methods=["GET"])
def get_meeting_time(engineer_id):
    db = get_db()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get meeting tasks for today
    meeting_tasks = list(db.tasks.find({
        'engineerId': engineer_id,
        'isMeeting': True,
        'meetingMetadata.startTime': {'$gte': today.isoformat()}
    }))
    
    # Calculate total meeting time
    total_meeting_time = sum((task.get('meetingMetadata', {}).get('duration', 0) for task in meeting_tasks), 0)
    
    # Analyze meeting overlap
    meetings_timeline = []
    for task in meeting_tasks:
        metadata = task.get('meetingMetadata', {})
        if metadata.get('startTime') and metadata.get('endTime'):
            meetings_timeline.append({
                'id': str(task['_id']),
                'title': task['title'],
                'start': datetime.fromisoformat(metadata['startTime']),
                'end': datetime.fromisoformat(metadata['endTime']),
                'duration': metadata.get('duration', 0),
                'isRecurring': metadata.get('isRecurring', False),
                'recurrencePattern': metadata.get('recurrencePattern')
            })
    
    # Sort meetings by start time
    meetings_timeline.sort(key=lambda x: x['start'])
    
    # Calculate overlap
    overlap_time = 0
    for i in range(len(meetings_timeline)):
        for j in range(i + 1, len(meetings_timeline)):
            meeting1 = meetings_timeline[i]
            meeting2 = meetings_timeline[j]
            if meeting1['end'] > meeting2['start']:
                overlap = min(meeting1['end'], meeting2['end']) - meeting2['start']
                overlap_time += overlap.total_seconds()
    
    # Analyze recurring patterns
    recurring_meetings = [m for m in meeting_tasks if m.get('meetingMetadata', {}).get('isRecurring', False)]
    recurring_patterns = {}
    for meeting in recurring_meetings:
        pattern = meeting['meetingMetadata']['recurrencePattern']
        recurring_patterns[pattern] = recurring_patterns.get(pattern, 0) + 1
    
    # Get idle time from monitoring sessions
    idle_time = sum(
        session.get('idleTime', 0)
        for session in db.monitoring_sessions.find({
            'engineerId': engineer_id,
            'startTime': {'$gte': today},
            'status': {'$in': ['stopped', 'idle']}
        })
    )
    
    # Convert datetime objects to ISO format for JSON serialization
    for meeting in meetings_timeline:
        meeting['start'] = meeting['start'].isoformat()
        meeting['end'] = meeting['end'].isoformat()
    
    return jsonify({
        'totalMeetingTime': total_meeting_time,
        'meetingCount': len(meeting_tasks),
        'idleTime': idle_time,
        'overlapTime': overlap_time,
        'meetings': meetings_timeline,
        'recurringMeetings': {
            'count': len(recurring_meetings),
            'patterns': recurring_patterns
        }
    }), 200
