"""
Configuration template for the application.
Copy this file to config.py and set the required environment variables.
DO NOT commit config.py to version control.
"""

import os

class Config:
    # Database Configuration
    MONGODB_URI = os.environ.get('MONGODB_URI')  # Required: MongoDB connection string
    MONGODB_DB = os.environ.get('MONGODB_DB')    # Required: Database name
    
    # Security Configuration
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')  # Required: GitHub API token with repo scope
    SECRET_KEY = os.environ.get('SECRET_KEY')      # Required: Random string for session encryption
    
    # Okta SSO Configuration
    OKTA_CLIENT_ID = os.environ.get('OKTA_CLIENT_ID')         # Required: Okta OAuth client ID
    OKTA_CLIENT_SECRET = os.environ.get('OKTA_CLIENT_SECRET') # Required: Okta OAuth client secret
    OKTA_ORG_URL = os.environ.get('OKTA_ORG_URL')            # Required: Okta organization URL
    OKTA_REDIRECT_URI = os.environ.get('OKTA_REDIRECT_URI')   # Required: OAuth callback URL
    
    # Azure AD SSO Configuration
    AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')         # Required: Azure AD client ID
    AZURE_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET') # Required: Azure AD client secret
    AZURE_TENANT_ID = os.environ.get('AZURE_TENANT_ID')        # Required: Azure AD tenant ID
    AZURE_REDIRECT_URI = os.environ.get('AZURE_REDIRECT_URI')   # Required: OAuth callback URL
    
    @classmethod
    def validate(cls):
        """Validate required configuration is present"""
        required = [
            'MONGODB_URI',
            'MONGODB_DB',
            'GITHUB_TOKEN',
            'SECRET_KEY'
        ]
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
