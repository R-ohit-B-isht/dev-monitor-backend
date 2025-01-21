from flask import Blueprint, jsonify, request, current_app
from pymongo import MongoClient
from datetime import datetime, timedelta
import re
from .utils.anonymization import hash_engineer_id

ai_bp = Blueprint("ai", __name__)

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

def analyze_code_complexity(code_diff):
    """Basic code complexity analysis"""
    # Count nested control structures
    control_keywords = ['if', 'for', 'while', 'try', 'with']
    nesting_level = 0
    max_nesting = 0
    lines = code_diff.split('\n')
    
    for line in lines:
        # Count indentation level
        indent = len(line) - len(line.lstrip())
        current_level = indent // 4  # Assuming 4 spaces per indent
        nesting_level = current_level
        
        # Check for control structures
        stripped = line.strip()
        if any(keyword in stripped for keyword in control_keywords):
            nesting_level += 1
        
        max_nesting = max(max_nesting, nesting_level)
    
    # Penalize high nesting levels
    complexity_score = max(0, 100 - (max_nesting * 10))
    return complexity_score

def analyze_code_readability(code_diff):
    """Basic code readability analysis"""
    lines = code_diff.split('\n')
    total_score = 0.0
    metrics = {
        'line_length': 0.0,
        'comment_ratio': 0.0,
        'naming_convention': 0.0
    }
    
    comment_count = 0
    total_lines = len(lines)
    
    for line in lines:
        # Line length score (penalize lines > 80 chars)
        line_length = len(line)
        metrics['line_length'] += float(min(100, max(0, 100 - (line_length - 80))))
        
        # Comment ratio
        if '#' in line or '"""' in line or "'''" in line:
            comment_count += 1
            
        # Variable naming conventions (snake_case for Python)
        if '=' in line:
            var_name = line.split('=')[0].strip()
            if re.match(r'^[a-z][a-z0-9_]*$', var_name):
                metrics['naming_convention'] += 100.0
                
    # Calculate final scores
    metrics['line_length'] = metrics['line_length'] / total_lines if total_lines > 0 else 0.0
    metrics['comment_ratio'] = (comment_count / total_lines * 100.0) if total_lines > 0 else 0.0
    metrics['naming_convention'] = metrics['naming_convention'] / total_lines if total_lines > 0 else 0.0
    
    # Weight the metrics
    total_score = (
        metrics['line_length'] * 0.4 +
        metrics['comment_ratio'] * 0.3 +
        metrics['naming_convention'] * 0.3
    )
    
    return total_score

@ai_bp.route("/ai/review-score", methods=["POST"])
def get_review_score():
    """Calculate code review score based on diff analysis"""
    try:
        data = request.json
        if not data or 'diff' not in data:
            return jsonify({'error': 'Code diff is required'}), 400
            
        code_diff = data['diff']
        
        # Calculate component scores
        complexity_score = analyze_code_complexity(code_diff)
        readability_score = analyze_code_readability(code_diff)
        
        # Calculate final score (weighted average)
        final_score = (complexity_score * 0.5) + (readability_score * 0.5)
        
        # Store the score in MongoDB
        db = get_db()
        score_record = {
            'timestamp': datetime.utcnow(),
            'complexity_score': complexity_score,
            'readability_score': readability_score,
            'final_score': final_score,
            'metadata': {
                'diff_size': len(code_diff),
                'repository': data.get('repository'),
                'pull_request': data.get('pull_request')
            }
        }
        db.code_scores.insert_one(score_record)
        
        return jsonify({
            'score': final_score,
            'details': {
                'complexity_score': complexity_score,
                'readability_score': readability_score
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to calculate review score: {str(e)}'}), 500

def suggest_next_tasks(activity_log):
    """Generate task suggestions based on activity history"""
    suggestions = []
    
    # Analyze activity patterns
    commit_count = sum(1 for activity in activity_log if activity.get('type') == 'commit')
    review_count = sum(1 for activity in activity_log if activity.get('type') == 'review')
    comment_count = sum(1 for activity in activity_log if activity.get('type') == 'comment')
    
    # Generate suggestions based on activity patterns
    if commit_count > 10 and review_count < 2:
        suggestions.append("Consider reviewing peers' code to maintain code quality")
    
    if review_count > 5 and commit_count < 2:
        suggestions.append("Focus on implementing new features or fixing bugs")
    
    if comment_count < 3 and (commit_count > 0 or review_count > 0):
        suggestions.append("Add more detailed comments to improve code documentation")
    
    # Add general productivity suggestions
    suggestions.extend([
        "Break down large tasks into smaller, manageable chunks",
        "Update task status regularly to maintain transparency",
        "Schedule regular code reviews to catch issues early"
    ])
    
    return {
        'suggestions': suggestions,
        'metrics': {
            'commit_count': commit_count,
            'review_count': review_count,
            'comment_count': comment_count
        },
        'timestamp': datetime.utcnow().isoformat()
    }

@ai_bp.route("/ai/suggestions/<engineer_id>", methods=["GET"])
def get_suggestions(engineer_id):
    """Get AI-generated task suggestions"""
    try:
        db = get_db()
        days = int(request.args.get('days', '7'))
        
        # Get recent activity
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        activity_log = list(db.activity_feed.find({
            'engineerId': hash_engineer_id(engineer_id),
            'timestamp': {'$gte': start_date, '$lt': end_date}
        }).sort('timestamp', -1))
        
        suggestions = suggest_next_tasks(activity_log)
        
        # Store suggestions
        db.ai_suggestions.insert_one({
            'engineerId': hash_engineer_id(engineer_id),
            'suggestions': suggestions['suggestions'],
            'metrics': suggestions['metrics'],
            'timestamp': datetime.utcnow(),
            'activityPeriod': {
                'start': start_date,
                'end': end_date
            }
        })
        
        return jsonify(suggestions), 200
    except Exception as e:
        return jsonify({'error': f'Failed to generate suggestions: {str(e)}'}), 500
