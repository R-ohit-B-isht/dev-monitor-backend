import os

class Config:
    # MongoDB Configuration
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
    MONGODB_DB = os.environ.get('MONGODB_DB', 'devin_tasks')
    
    # Security
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Okta SSO Configuration
    OKTA_CLIENT_ID = os.environ.get('OKTA_CLIENT_ID')
    OKTA_CLIENT_SECRET = os.environ.get('OKTA_CLIENT_SECRET')
    OKTA_ORG_URL = os.environ.get('OKTA_ORG_URL')
    OKTA_REDIRECT_URI = os.environ.get('OKTA_REDIRECT_URI', 'http://localhost:5000/sso/callback/okta')
    
    # Azure AD SSO Configuration
    AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')
    AZURE_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET')
    AZURE_TENANT_ID = os.environ.get('AZURE_TENANT_ID')
    AZURE_REDIRECT_URI = os.environ.get('AZURE_REDIRECT_URI', 'http://localhost:5000/sso/callback/azure')
    
    # Email Configuration
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
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
