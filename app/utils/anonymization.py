from hashlib import sha256
import base64
import re

def hash_engineer_id(engineer_id: str | None) -> str:
    """Hash engineer ID using SHA-256"""
    if not engineer_id:
        return "anonymous"
    return sha256(str(engineer_id).encode('utf-8')).hexdigest()

def obfuscate_email(email: str) -> str:
    """Obfuscate email address while preserving domain"""
    if not email or '@' not in email:
        return email
    
    username, domain = email.split('@')
    if len(username) <= 2:
        obfuscated = username[0] + '*' * (len(username) - 1)
    else:
        obfuscated = username[0] + '*' * (len(username) - 2) + username[-1]
    
    return f"{obfuscated}@{domain}"

def obfuscate_repository_name(repo_name: str) -> str:
    """Obfuscate repository name while preserving owner"""
    if not repo_name or '/' not in repo_name:
        return repo_name
    
    owner, name = repo_name.split('/')
    if len(name) <= 2:
        obfuscated = name[0] + '*' * (len(name) - 1)
    else:
        obfuscated = name[0] + '*' * (len(name) - 2) + name[-1]
    
    return f"{owner}/{obfuscated}"

def obfuscate_commit_message(message: str) -> str:
    """Obfuscate potentially sensitive information in commit messages"""
    # Remove email addresses
    message = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL]', message)
    
    # Remove API keys and tokens
    message = re.sub(r'[\'"`][0-9a-zA-Z]{32,}[\'"`]', '[API_KEY]', message)
    
    # Remove IP addresses
    message = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]', message)
    
    return message

def generate_anonymous_id(prefix: str = '') -> str:
    """Generate a random anonymous ID with optional prefix"""
    random_bytes = base64.urlsafe_b64encode(sha256(str(hash(prefix)).encode()).digest())[:8]
    return f"{prefix}_{random_bytes.decode('utf-8')}" if prefix else random_bytes.decode('utf-8')
