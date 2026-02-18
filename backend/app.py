# ============================================================
# backend/app.py — Flask Application Factory
# ============================================================
# This is the main entry point for the backend server.
#
# Architecture overview:
#   1. Create the Flask app.
#   2. Load configuration from config.py.
#   3. Initialize extensions (MongoDB).
#   4. Register blueprints (route groups).
#   5. Mount Swagger UI for API documentation.
#
# To run:
#   cd backend
#   python app.py
#
# Or from project root:
#   python -m backend.app
# ============================================================

import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

# Ensure the project root is on the Python path so we can import
# backend modules cleanly with "from backend.xxx import yyy"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.config import Config
from backend.extensions import init_db
from backend.routes.workflow_routes import workflow_bp
from backend.routes.generated_routes import generated_bp
from backend.routes.docs_routes import docs_bp


def create_app():
    """
    Application factory function.

    Creates and configures a Flask application instance.
    This pattern makes the app easier to test and allows
    creating multiple instances if needed.

    Returns:
        Flask: Configured Flask application.
    """
    # --- Step 1: Create the Flask app ---
    app = Flask(__name__)

    # --- Step 2: Load configuration ---
    app.config['MONGO_URI'] = Config.MONGO_URI
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['DEBUG'] = Config.DEBUG

    # --- Step 3: Enable CORS ---
    # Allow the React frontend (ports 5173-5174) to call the backend (port 5000)
    # Multiple ports to handle different Vite dev server instances
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173", 
                "http://127.0.0.1:5173",
                "http://localhost:5174",
                "http://127.0.0.1:5174"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    # --- Step 4: Initialize MongoDB ---
    init_db(app)

    # --- Step 5: Register route blueprints ---
    # Each blueprint is a modular group of related routes.
    app.register_blueprint(workflow_bp)     # /api/workflows/...
    app.register_blueprint(generated_bp)    # /api/generated/...
    app.register_blueprint(docs_bp)         # /api/docs/...

    # --- Step 6: Mount Swagger UI ---
    # Serves an interactive API documentation page at /swagger/
    # It reads the spec from our /api/docs/openapi.json endpoint
    swagger_ui = get_swaggerui_blueprint(
        '/swagger',                     # URL where Swagger UI will be served
        '/api/docs/openapi.json',       # URL of our OpenAPI spec
        config={
            'app_name': 'Low-Code API Builder — Swagger Docs'
        }
    )
    app.register_blueprint(swagger_ui, url_prefix='/swagger')

    # --- Step 7: Health check / root route ---
    @app.route('/')
    def health_check():
        """Simple health check endpoint."""
        return jsonify({
            'status': 'running',
            'service': 'Low-Code API Builder Platform',
            'version': '1.0.0',
            'endpoints': {
                'workflows': '/api/workflows',
                'generated': '/api/generated/<workflow_name>',
                'docs': '/swagger/',
                'openapi_spec': '/api/docs/openapi.json',
            }
        }), 200

    # --- Step 8: Global error handlers ---
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource does not exist.'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred.'
        }), 500

    return app


# ============================================================
# Main entry point — run the dev server
# ============================================================
if __name__ == '__main__':
    app = create_app()
    print("\n" + "=" * 60)
    print("  🚀 Low-Code API Builder Platform")
    print("=" * 60)
    print(f"  Server:    http://localhost:{Config.PORT}")
    print(f"  Swagger:   http://localhost:{Config.PORT}/swagger/")
    print(f"  MongoDB:   {Config.MONGO_URI}")
    print("=" * 60 + "\n")
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.DEBUG
    )
