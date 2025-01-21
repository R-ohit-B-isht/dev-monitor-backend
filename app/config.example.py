"""
Developer Productivity Monitor Configuration
-----------------------------------------

This is a template for configuring the Developer Productivity Monitor.
Copy this file to config.py and set the required environment variables.

Security Notice:
---------------
1. Never commit config.py to version control
2. Use strong, unique values for all secrets and tokens
3. Follow the principle of least privilege when setting up service accounts
4. Regularly rotate all access tokens and secrets
5. Use separate credentials for development and production

Required Environment Variables:
-----------------------------
MONGODB_URI: MongoDB connection string
MONGODB_DB: MongoDB database name
SECRET_KEY: Flask secret key (use a strong random value)
GITHUB_TOKEN: GitHub API token with repo and user scopes
DEVIN_API_KEY: Devin AI API key for AI integrations
JIRA_DOMAIN: Jira domain (e.g., company.atlassian.net)
JIRA_EMAIL: Jira account email
JIRA_API_TOKEN: Jira API token
LINEAR_API_TOKEN: Linear API token
GITHUB_API_TOKEN: GitHub API token

Optional Environment Variables:
----------------------------
DEBUG: Enable debug mode (default: False)
TESTING: Enable testing mode (default: False)
CORS_ORIGINS: Comma-separated list of allowed origins (default: *)
WS_PING_INTERVAL: WebSocket ping interval in seconds (default: 25)
WS_PING_TIMEOUT: WebSocket ping timeout in seconds (default: 120)
"""

import os

class Config:
    # MongoDB Configuration
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
    MONGODB_DB = os.environ.get('MONGODB_DB', 'devin_tasks')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Devin AI Configuration
    DEVIN_API_URL = os.environ.get('DEVIN_API_URL', 'https://api.devin.ai/v1/sessions')
    DEVIN_API_KEY = os.environ.get('DEVIN_API_KEY')
    
    # Jira Configuration
    JIRA = {
       "domain": os.environ.get('JIRA_DOMAIN'),
       "email": os.environ.get('JIRA_EMAIL'),
       "api_token": os.environ.get('JIRA_API_TOKEN')
    }
    
    # Linear Configuration
    LINEAR = {
        "api_token": os.environ.get('LINEAR_API_TOKEN')
    }
    
    # GitHub Configuration
    GITHUB = {
        "api_token": os.environ.get('GITHUB_API_TOKEN')
    }
    
    # SSO Configuration
    OKTA_CLIENT_ID = os.environ.get('OKTA_CLIENT_ID')
    OKTA_CLIENT_SECRET = os.environ.get('OKTA_CLIENT_SECRET')
    OKTA_ORG_URL = os.environ.get('OKTA_ORG_URL')
    OKTA_REDIRECT_URI = os.environ.get('OKTA_REDIRECT_URI')
    
    AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')
    AZURE_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET')
    AZURE_TENANT_ID = os.environ.get('AZURE_TENANT_ID')
    AZURE_REDIRECT_URI = os.environ.get('AZURE_REDIRECT_URI')
    
    # Email Configuration
    SMTP_SERVER = os.environ.get('SMTP_SERVER')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    
    # Slack Configuration
    SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
    SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET')
    
    # Development Settings
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    TESTING = os.environ.get('TESTING', 'False').lower() == 'true'
    
    # CORS Settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # WebSocket Settings
    WS_PING_INTERVAL = int(os.environ.get('WS_PING_INTERVAL', '25'))
    WS_PING_TIMEOUT = int(os.environ.get('WS_PING_TIMEOUT', '120'))

    # Devin AI Configuration
    DEVIN_API_URL = os.environ.get('DEVIN_API_URL', 'https://api.devin.ai')
    DEVIN_API_KEY = os.environ.get('DEVIN_API_KEY')

    # Linear Configuration
    LINEAR_API_TOKEN = os.environ.get('LINEAR_API_TOKEN')
    LINEAR = {
        'api_token': LINEAR_API_TOKEN
    }

    # Jira Configuration
    JIRA_DOMAIN = os.environ.get('JIRA_DOMAIN')
    JIRA_EMAIL = os.environ.get('JIRA_EMAIL')
    JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN')
    JIRA = {
        'domain': JIRA_DOMAIN,
        'email': JIRA_EMAIL,
        'api_token': JIRA_API_TOKEN
    }

    # Integration Filters Configuration
    FILTERS = {
        'linear': {
            'trigger_mention': '@devin',
            'prompt_template': 'Analyze this Linear issue:\nComment: {comment}\nTitle: {issue_title}\nDescription: {issue_description}'
        },
        'jira': {
            'trigger_mention': '@devin',
            'prompt_template': 'Analyze this Jira issue:\nComment: {comment}\nSummary: {issue_summary}\nDescription: {issue_description}'
        }
    }
