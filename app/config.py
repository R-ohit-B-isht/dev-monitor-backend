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
        "api_token": os.environ.get("Github_Personal_Access_Token")
    }

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

    # Integration filters
    FILTERS = {
        "jira": {
            "trigger_mention": "@devin",
            "prompt_template": """
            User Prompt: {comment}
            Issue Summary: {issue_summary}
            Issue Description: {issue_description}
            """,
        },
        "linear": {
            "trigger_mention": "@devin",
            "prompt_template": """
            User Prompt: {comment}
            Issue Title: {issue_title}
            Issue Description: {issue_description}
            """,
        },
        "github": {
            "trigger_mention": "@devin-ai-integration",
            "prompt_template": """
            Issue URL: {url}
            User Prompt: {comment}
            Issue: {issue}
            """,
        },
    }
