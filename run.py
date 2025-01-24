from app import create_app
from flask_socketio import SocketIO
import os

# Debug: Print environment variables
print("Environment variables:")
print("Github_Personal_Access_Token:", os.environ.get("Github_Personal_Access_Token"))

app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*")

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000, host='0.0.0.0', use_reloader=True, log_output=True, allow_unsafe_werkzeug=True)
