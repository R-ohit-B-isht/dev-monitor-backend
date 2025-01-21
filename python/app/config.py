import os

class Config:
    MONGODB_URI = "mongodb://localhost:27017"
    MONGODB_DB = "devin_tasks"
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    
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
