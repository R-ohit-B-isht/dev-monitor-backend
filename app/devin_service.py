import requests
from flask import current_app

def trigger_devin_session(prompt):
    """Trigger a Devin AI session with the given prompt"""
    url = current_app.config["DEVIN_API_URL"]
    api_key = current_app.config["DEVIN_API_KEY"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "idempotent": True,
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json() if response.status_code == 200 else {"error": response.text}
