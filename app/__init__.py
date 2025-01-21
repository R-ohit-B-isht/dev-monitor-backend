from flask import Flask, current_app
from flask_cors import CORS
from pymongo import MongoClient
from .websocket_service import websocket_bp, init_websocket

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

def init_collections(db):
    """Initialize MongoDB collections and indexes"""
    # Performance events collection
    if 'performance_events' not in db.list_collection_names():
        db.create_collection('performance_events')
    db.performance_events.create_index([('timestamp', -1)])
    db.performance_events.create_index([('engineerId', 1)])
    db.performance_events.create_index([('type', 1)])
    db.performance_events.create_index([('severity', 1)])

    # Git events collection
    if 'git_events' not in db.list_collection_names():
        db.create_collection('git_events')
    db.git_events.create_index([('timestamp', -1)])
    db.git_events.create_index([('taskId', 1)])
    db.git_events.create_index([('sha', 1)])
    db.git_events.create_index([('type', 1)])
    
    # Code scores collection
    if 'code_scores' not in db.list_collection_names():
        db.create_collection('code_scores')
    db.code_scores.create_index([('timestamp', -1)])
    db.code_scores.create_index([('final_score', 1)])
    db.code_scores.create_index([('metadata.repository', 1)])

    # Deploy events collection
    if 'deploy_events' not in db.list_collection_names():
        db.create_collection('deploy_events')
    db.deploy_events.create_index([('timestamp', -1)])
    db.deploy_events.create_index([('taskId', 1)])
    db.deploy_events.create_index([('status', 1)])
    db.deploy_events.create_index([('environment', 1)])

    # Users collection for RBAC
    if 'users' not in db.list_collection_names():
        db.create_collection('users')
    db.users.create_index([('username', 1)], unique=True)
    db.users.create_index([('email', 1)], unique=True)
    db.users.create_index([('role', 1)])
    
    # Achievements collection
    if 'achievements' not in db.list_collection_names():
        db.create_collection('achievements')
    db.achievements.create_index([('engineerId', 1)])
    db.achievements.create_index([('badge', 1)])
    db.achievements.create_index([('type', 1)])
    db.achievements.create_index([('earnedAt', -1)])

def create_app(register_blueprints=True):
    app = Flask(__name__)
    CORS(app, resources={
        r"/*": {
            "origins": ["*"],  # Allow all origins in development
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    app.config.from_object("app.config.Config")

    if register_blueprints:
        # Register routes
        with app.app_context():
            from .routes import webhook_bp
            from .task_service import tasks_bp
            from .relationship_service import relationships_bp
            from .mindmap_service import mindmap_bp
            from .monitoring_service import monitoring_bp
            from .schedule_service import schedule_bp, start_monitoring_thread
            from .leaderboard_service import leaderboard_bp
            from .report_service import report_bp
            from .settings_service import settings_bp
            from .dora_service import dora_bp
            from .value_stream_service import value_stream_bp
            from .git_service import git_bp
            from .security_service import security_bp, init_collections as init_security_collections
            from .auth_service import auth_bp
            from .collaboration_service import collab_bp, init_collections as init_collab_collections
            from .ai_service import ai_bp
            from .notifications_service import notifications_bp, init_collections as init_notifications_collections
            from .sso_service import sso_bp, init_collections as init_sso_collections
            from .achievements_service import achievements_bp
            app.register_blueprint(webhook_bp)
            app.register_blueprint(tasks_bp)
            app.register_blueprint(relationships_bp)
            app.register_blueprint(mindmap_bp)
            app.register_blueprint(monitoring_bp)
            app.register_blueprint(schedule_bp)
            app.register_blueprint(leaderboard_bp)
            app.register_blueprint(report_bp)
            app.register_blueprint(settings_bp)
            app.register_blueprint(dora_bp)
            app.register_blueprint(value_stream_bp)
            app.register_blueprint(git_bp)
            app.register_blueprint(security_bp)
            app.register_blueprint(auth_bp)
            app.register_blueprint(collab_bp)
            app.register_blueprint(ai_bp)
            app.register_blueprint(notifications_bp)
            app.register_blueprint(sso_bp)
            app.register_blueprint(achievements_bp)
            app.register_blueprint(websocket_bp)
            
            # Initialize WebSocket
            socketio = init_websocket(app)
            
            # Initialize collections
            db = get_db()
            init_collections(db)
            init_security_collections(db)
            init_collab_collections(db)
            init_notifications_collections(db)
            init_sso_collections(db)
            
            # Start background monitoring threads
            from .schedule_service import start_monitoring_thread
            from .monitoring_service import start_performance_monitoring
            start_monitoring_thread(app)
            start_performance_monitoring(app)

    return app
