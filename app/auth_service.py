from flask import Blueprint, jsonify, request, current_app, session
from functools import wraps
from enum import Enum
import jwt
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)

class UserRole(Enum):
    ADMIN = "admin"
    SECURITY_MANAGER = "security_manager"
    REVIEWER = "reviewer"
    DEVELOPER = "developer"
    VIEWER = "viewer"

def get_db():
    from pymongo import MongoClient
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

def init_collections(db):
    """Ensure required collections exist with proper indexes"""
    if 'users' not in db.list_collection_names():
        db.create_collection('users')
    db.users.create_index([('username', 1)], unique=True)
    db.users.create_index([('email', 1)], unique=True)

def check_role(required_roles):
    """Decorator to check if user has required role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not isinstance(required_roles, (list, tuple)):
                roles_to_check = [required_roles]
            else:
                roles_to_check = required_roles

            user_role = session.get('user_role')
            if not user_role or user_role not in [r.value for r in roles_to_check]:
                return jsonify({
                    'error': 'Forbidden',
                    'message': 'Insufficient permissions'
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def generate_token(user_id, role):
    """Generate JWT token for user"""
    payload = {
        'user_id': str(user_id),
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify JWT token and return payload"""
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    """Register a new user"""
    db = get_db()
    data = request.json

    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if user already exists
    if db.users.find_one({'$or': [
        {'username': data['username']},
        {'email': data['email']}
    ]}):
        return jsonify({'error': 'User already exists'}), 409

    # Create new user with default role
    user = {
        'username': data['username'],
        'email': data['email'],
        'password': data['password'],  # Note: Should be hashed in production
        'role': UserRole.DEVELOPER.value,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    result = db.users.insert_one(user)
    token = generate_token(result.inserted_id, user['role'])

    return jsonify({
        'token': token,
        'user': {
            'id': str(result.inserted_id),
            'username': user['username'],
            'email': user['email'],
            'role': user['role']
        }
    }), 201

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """Login user and return token"""
    db = get_db()
    data = request.json

    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400

    user = db.users.find_one({'username': data['username']})
    if not user or user['password'] != data['password']:  # Note: Should use proper password comparison in production
        return jsonify({'error': 'Invalid credentials'}), 401

    token = generate_token(user['_id'], user['role'])
    
    return jsonify({
        'token': token,
        'user': {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role']
        }
    }), 200

@auth_bp.route("/auth/verify", methods=["GET"])
def verify():
    """Verify token and return user info"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid token'}), 401

    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401

    db = get_db()
    user = db.users.find_one({'_id': payload['user_id']})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'user': {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role']
        }
    }), 200

# Example protected route
@auth_bp.route("/auth/test-admin", methods=["GET"])
@check_role(UserRole.ADMIN)
def test_admin():
    """Test route for admin access"""
    return jsonify({'message': 'Admin access granted'}), 200

# Example route with multiple allowed roles
@auth_bp.route("/auth/test-security", methods=["GET"])
@check_role([UserRole.ADMIN, UserRole.SECURITY_MANAGER])
def test_security():
    """Test route for security access"""
    return jsonify({'message': 'Security access granted'}), 200
