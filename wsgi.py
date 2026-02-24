# ============================================================
# wsgi.py — Production WSGI Entry Point
# ============================================================
# Gunicorn imports this file to get the Flask app instance.
# This avoids shell escaping issues with create_app() in the
# start command.
#
# Usage:  gunicorn wsgi:app --bind 0.0.0.0:$PORT
# ============================================================

from backend.app import create_app

app = create_app()
