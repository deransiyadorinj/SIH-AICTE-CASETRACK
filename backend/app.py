import os
import sys
from pathlib import Path
from flask import Flask, jsonify
from flask_cors import CORS

# Ensure root workspace is in sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR.parent))

from backend.config import Config
from backend.database import close_db, init_tables
from backend.init_db import seed_database

from backend.routes.auth_routes import auth_bp
from backend.routes.complaint_routes import complaint_bp
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.bureau_routes import bureau_bp
from backend.routes.report_routes import report_bp
from backend.routes.notification_routes import notification_bp
from backend.routes.audit_routes import audit_bp
from backend.routes.user_routes import user_bp
from backend.routes.admin_panel import admin_panel_bp

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    # Initialize tables and seed data if db is missing
    seed_database()

    # Enable CORS
    CORS(
        app,
        resources={r"/api/*": {"origins": Config.CORS_ORIGINS}},
        supports_credentials=True,
        expose_headers=["Content-Disposition"]
    )

    # Register teardown
    app.teardown_appcontext(close_db)

    # Health check
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'AICTE CASETRACK API',
            'version': '1.0.0',
            'database': 'connected'
        })

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(complaint_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(bureau_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_panel_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'message': 'Resource not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting AICTE CaseTrack Backend Server on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
