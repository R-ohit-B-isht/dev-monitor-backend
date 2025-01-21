from flask import Blueprint, jsonify, request, current_app, url_for, redirect, session
from pymongo import MongoClient
from datetime import datetime, timedelta
import jwt
import requests
from .utils.anonymization import hash_engineer_id

sso_bp = Blueprint("sso", __name__)

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

def init_collections(db):
    """Initialize MongoDB collections and indexes for SSO"""
    if 'sso_sessions' not in db.list_collection_names():
        db.create_collection('sso_sessions')
    db.sso_sessions.create_index([('created_at', -1)])
    db.sso_sessions.create_index([('user_id', 1)])
    db.sso_sessions.create_index([('provider', 1)])

class OktaProvider:
    def __init__(self, app_config):
        self.client_id = app_config.get('OKTA_CLIENT_ID')
        self.client_secret = app_config.get('OKTA_CLIENT_SECRET')
        self.org_url = app_config.get('OKTA_ORG_URL')
        self.redirect_uri = app_config.get('OKTA_REDIRECT_URI')

    def get_authorization_url(self):
        return f"{self.org_url}/oauth2/v1/authorize?" + \
               f"client_id={self.client_id}&" + \
               f"response_type=code&" + \
               f"scope=openid profile email&" + \
               f"redirect_uri={self.redirect_uri}&" + \
               f"state={hash_engineer_id(str(datetime.utcnow()))}"

    def get_token(self, code):
        token_url = f"{self.org_url}/oauth2/v1/token"
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        response = requests.post(token_url, data=data)
        return response.json()

    def get_user_info(self, access_token):
        userinfo_url = f"{self.org_url}/oauth2/v1/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(userinfo_url, headers=headers)
        return response.json()

class AzureADProvider:
    def __init__(self, app_config):
        self.client_id = app_config.get('AZURE_CLIENT_ID')
        self.client_secret = app_config.get('AZURE_CLIENT_SECRET')
        self.tenant_id = app_config.get('AZURE_TENANT_ID')
        self.redirect_uri = app_config.get('AZURE_REDIRECT_URI')

    def get_authorization_url(self):
        return f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize?" + \
               f"client_id={self.client_id}&" + \
               f"response_type=code&" + \
               f"scope=openid profile email&" + \
               f"redirect_uri={self.redirect_uri}&" + \
               f"state={hash_engineer_id(str(datetime.utcnow()))}"

    def get_token(self, code):
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        response = requests.post(token_url, data=data)
        return response.json()

    def get_user_info(self, access_token):
        userinfo_url = "https://graph.microsoft.com/v1.0/me"
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(userinfo_url, headers=headers)
        return response.json()

@sso_bp.route("/sso/login/<provider>")
def login(provider):
    """Initiate SSO login flow"""
    try:
        if provider == 'okta':
            provider_client = OktaProvider(current_app.config)
        elif provider == 'azure':
            provider_client = AzureADProvider(current_app.config)
        else:
            return jsonify({'error': 'Unsupported SSO provider'}), 400

        auth_url = provider_client.get_authorization_url()
        return redirect(auth_url)
    except Exception as e:
        return jsonify({'error': f'Failed to initiate SSO login: {str(e)}'}), 500

@sso_bp.route("/sso/callback/<provider>")
def callback(provider):
    """Handle SSO callback"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code:
            return jsonify({'error': 'Authorization code missing'}), 400
            
        if provider == 'okta':
            provider_client = OktaProvider(current_app.config)
        elif provider == 'azure':
            provider_client = AzureADProvider(current_app.config)
        else:
            return jsonify({'error': 'Unsupported SSO provider'}), 400
            
        # Exchange code for token
        token_response = provider_client.get_token(code)
        access_token = token_response.get('access_token')
        
        if not access_token:
            return jsonify({'error': 'Failed to obtain access token'}), 400
            
        # Get user info
        user_info = provider_client.get_user_info(access_token)
        
        # Store session
        db = get_db()
        session_data = {
            'user_id': user_info.get('sub') or user_info.get('id'),
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'provider': provider,
            'access_token': access_token,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=1)
        }
        
        db.sso_sessions.insert_one(session_data)
        
        # Generate JWT for frontend
        jwt_token = jwt.encode(
            {
                'sub': session_data['user_id'],
                'email': session_data['email'],
                'name': session_data['name'],
                'exp': session_data['expires_at']
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        return jsonify({
            'token': jwt_token,
            'user': {
                'id': session_data['user_id'],
                'email': session_data['email'],
                'name': session_data['name']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'SSO callback failed: {str(e)}'}), 500

@sso_bp.route("/sso/logout")
def logout():
    """Handle SSO logout"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        # Decode token to get user info
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
        # Remove session
        db = get_db()
        db.sso_sessions.delete_many({
            'user_id': payload['sub'],
            'expires_at': {'$gt': datetime.utcnow()}
        })
        
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500
