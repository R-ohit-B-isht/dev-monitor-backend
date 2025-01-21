from flask import Blueprint, jsonify, request, current_app
from pymongo import MongoClient
from datetime import datetime
import re

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
