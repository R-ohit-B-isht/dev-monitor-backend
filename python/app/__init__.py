from flask import Flask
from flask_cors import CORS

def create_app(register_blueprints=True):
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
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
            app.register_blueprint(webhook_bp)
            app.register_blueprint(tasks_bp)
            app.register_blueprint(relationships_bp)
            app.register_blueprint(mindmap_bp)
            app.register_blueprint(monitoring_bp)
            app.register_blueprint(schedule_bp)
            app.register_blueprint(leaderboard_bp)
            app.register_blueprint(report_bp)
            
            # Start background monitoring thread
            start_monitoring_thread(app)

    return app
