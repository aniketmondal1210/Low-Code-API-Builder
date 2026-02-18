# ============================================================
# backend/extensions.py — Shared Extension Instances
# ============================================================
# We create extension instances here (instead of in app.py) so
# that other modules can import them without circular imports.
#
# Pattern:
#   1. Create the instance here (uninitialised).
#   2. In app.py, call init_app(app) to bind it to the Flask app.
#   3. Other modules just `from extensions import db`.
#
# If MongoDB is not running, the app still starts but all DB
# operations return a clear error message instead of crashing.
# ============================================================

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

# This will hold the MongoDB client and database reference.
# Initialised properly in app.py after reading config.
mongo_client = None   # type: MongoClient | None
db = None             # type: any  — will be a pymongo.database.Database
db_available = False  # Track whether MongoDB is reachable


def init_db(app):
    """
    Initialise the MongoDB connection using the app's config.

    Called once during app startup in app.py.
    After this runs, other modules can simply do:
        from backend.extensions import db
        db.workflows.find(...)

    If MongoDB is not running, the app still starts but logs
    a clear warning. All DB operations will fail gracefully.
    """
    global mongo_client, db, db_available

    mongo_uri = app.config['MONGO_URI']

    # Extract database name from the URI.
    # Atlas URIs look like: mongodb+srv://user:pass@cluster.xxx.net/api_builder?retryWrites=true
    # We need to parse out just "api_builder", stripping query params.
    from urllib.parse import urlparse
    parsed = urlparse(mongo_uri)
    db_name = parsed.path.lstrip('/')  # "/api_builder" → "api_builder"
    if not db_name:
        db_name = 'api_builder'  # Fallback default

    try:
        # Create the client with a short timeout so we fail fast
        mongo_client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
        )

        # Actually verify the connection works RIGHT NOW
        mongo_client.admin.command('ping')

        # Connection succeeded — set the database reference
        db = mongo_client[db_name]
        db_available = True
        app.logger.info(f"✅ Connected to MongoDB database: {db_name}")

    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        # MongoDB is not running — log a clear error but don't crash
        db_available = False
        db = None
        app.logger.warning(
            "\n" + "=" * 60 +
            "\n  ⚠️  MongoDB is NOT running!" +
            "\n" + "=" * 60 +
            f"\n  Tried to connect to: {mongo_uri}" +
            f"\n  Error: {e}" +
            "\n" +
            "\n  The server will start, but all database operations" +
            "\n  will return errors until MongoDB is available." +
            "\n" +
            "\n  To fix this:" +
            "\n    1. Install MongoDB: https://www.mongodb.com/try/download/community" +
            "\n    2. Start MongoDB:   mongod" +
            "\n    3. Restart this server: python backend/app.py" +
            "\n" + "=" * 60 + "\n"
        )

    except Exception as e:
        db_available = False
        db = None
        app.logger.error(f"❌ Unexpected MongoDB error: {e}")


def require_db():
    """
    Helper that checks if MongoDB is available.

    Call this at the top of any route that needs the database.
    Returns (True, None) if OK, or (False, error_response_tuple) if not.

    Usage in a route:
        ok, error = require_db()
        if not ok:
            return error
    """
    if not db_available or db is None:
        from flask import jsonify
        return False, (jsonify({
            'error': 'Database Unavailable',
            'message': (
                'MongoDB is not running. Please start MongoDB and '
                'restart the server. See terminal logs for instructions.'
            ),
        }), 503)
    return True, None
