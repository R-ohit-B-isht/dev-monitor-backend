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
    if not code_diff:
        return 100  # Empty code has perfect complexity score
        
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
        if any(f"{keyword} " in f"{stripped} " for keyword in control_keywords):
            nesting_level += 1
        
        max_nesting = max(max_nesting, nesting_level)
    
    # Penalize high nesting levels
    complexity_score = max(0, 100 - (max_nesting * 10))
    return complexity_score

def analyze_code_readability(code_diff):
    """Basic code readability analysis"""
    if not code_diff:
        return 0  # Empty code has zero readability score
        
    # Handle both string and list input
    if isinstance(code_diff, list):
        lines = [line for line in code_diff if line.strip()]
    else:
        lines = [line for line in code_diff.split('\n') if line.strip()]
        
    if not lines:
        return 0
        
    total_score = 0.0
    metrics = {
        'line_length': 0.0,
        'comment_quality': 0.0,
        'naming_convention': 0.0,
        'code_structure': 0.0
    }
    
    comment_lines = []
    total_lines = len(lines)
    var_names = []
    func_names = []
    indentation_consistent = True
    prev_indent = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
            
        # Line length score (penalize lines > 80 chars)
        line_length = len(line)
        metrics['line_length'] += float(min(100, max(0, 100 - (line_length - 80))))
        
        # Check indentation consistency
        if stripped:
            indent = len(line) - len(line.lstrip())
            if prev_indent is not None and indent % 4 != 0:
                indentation_consistent = False
            prev_indent = indent
        
        # Collect comments
        if (stripped.startswith('#') or 
            stripped.startswith('"""') or 
            stripped.startswith("'''") or 
            '# ' in line):
            comment_lines.append(stripped)
            
        # Collect variable and function names
        if '=' in line and not stripped.startswith('#'):
            var_name = line.split('=')[0].strip()
            var_names.append(var_name)
            
        if stripped.startswith('def '):
            func_name = stripped[4:].split('(')[0].strip()
            func_names.append(func_name)
                
    # Calculate comment quality score
    comment_score = 0
    meaningful_comments = 0
    function_has_docstring = False
    
    for comment in comment_lines:
        # Remove comment markers
        text = comment.lstrip('#').lstrip('"').lstrip("'").strip()
        
        # Check for function docstring
        if any(line.strip().startswith('def ') for line in lines):
            if '"""' in comment or "'''" in comment:
                function_has_docstring = True
                comment_score += 30  # Bonus for having docstring
        
        # Check if comment is meaningful
        if len(text.split()) > 2 and not text.startswith('TODO'):
            meaningful_comments += 1
            # Bonus for descriptive comments
            if len(text) > 20:
                comment_score += 25
            elif len(text) > 10:
                comment_score += 15
                
    # Bonus for good comment ratio
    comment_ratio = len(comment_lines) / max(1, len(lines))
    if comment_ratio >= 0.2:  # At least 20% comments
        comment_score += 30
    elif comment_ratio >= 0.1:  # At least 10% comments
        comment_score += 15
        
    metrics['comment_quality'] = min(100, comment_score)
    
    # Calculate naming convention score
    naming_score = 0
    total_names = len(var_names) + len(func_names)
    if total_names > 0:
        for name in var_names + func_names:
            # Base score for snake_case
            if re.match(r'^[a-z][a-z0-9_]*$', name):
                naming_score += 50  # Increased base score
                
                # Bonus for descriptive length
                if len(name) > 2:
                    naming_score += 15
                if len(name) > 8:
                    naming_score += 15
                    
                # Bonus for meaningful word separation
                if '_' in name:
                    naming_score += 20
                        
                # Penalty for overly short names
                if len(name) <= 2:
                    naming_score -= 30
            else:
                # Penalty for non-snake_case
                naming_score -= 20
                
        # Average the score across all names
        naming_score = naming_score / total_names
    else:
        naming_score = 100  # No names to check
        
    metrics['naming_convention'] = max(0, min(100, naming_score))
    
    # Calculate code structure score
    structure_score = 100
    if not indentation_consistent:
        structure_score -= 30
    if total_lines > 3:
        # Penalize for no comments in longer code
        if not comment_lines:
            structure_score -= 30  # Reduced penalty
        # Penalize for too dense code
        if len(comment_lines) < total_lines / 15:  # Relaxed ratio
            structure_score -= 15
    
    # Bonus for having docstring in functions
    if function_has_docstring:
        structure_score = min(100, structure_score + 20)
        
    metrics['code_structure'] = max(0, structure_score)
    
    # Calculate final scores
    metrics['line_length'] = metrics['line_length'] / total_lines if total_lines > 0 else 100.0
    
    # Weight the metrics (adjusted weights)
    total_score = (
        metrics['line_length'] * 0.15 +
        metrics['comment_quality'] * 0.40 +  # Increased weight for comments
        metrics['naming_convention'] * 0.25 +
        metrics['code_structure'] * 0.20
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
