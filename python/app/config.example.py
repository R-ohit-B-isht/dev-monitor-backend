import os

class Config:
    # Database Configuration
    MONGODB_URI = os.environ.get('MONGODB_URI')  # Required: MongoDB connection string
    MONGODB_DB = os.environ.get('MONGODB_DB')    # Required: Database name
    
    # Security Configuration
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')  # Required: GitHub API token
    SECRET_KEY = os.environ.get('SECRET_KEY')      # Required: App secret key
    
    # Okta SSO Configuration
    OKTA_CLIENT_ID = os.environ.get('OKTA_CLIENT_ID')         # Required for Okta SSO
    OKTA_CLIENT_SECRET = os.environ.get('OKTA_CLIENT_SECRET') # Required for Okta SSO
    OKTA_ORG_URL = os.environ.get('OKTA_ORG_URL')            # Required for Okta SSO
    OKTA_REDIRECT_URI = os.environ.get('OKTA_REDIRECT_URI')   # Required for Okta SSO
    
    # Azure AD SSO Configuration
    AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')         # Required for Azure SSO
    AZURE_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET') # Required for Azure SSO
    AZURE_TENANT_ID = os.environ.get('AZURE_TENANT_ID')        # Required for Azure SSO
    AZURE_REDIRECT_URI = os.environ.get('AZURE_REDIRECT_URI')   # Required for Azure SSO
