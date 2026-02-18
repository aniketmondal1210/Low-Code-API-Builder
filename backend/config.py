# ============================================================
# backend/config.py — Application Configuration
# ============================================================
# Reads environment variables from .env and exposes them as
# constants that the rest of the app can import.
# ============================================================

import os
from dotenv import load_dotenv

# Load variables from the .env file at project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


class Config:
    """
    Central configuration class.

    All settings are read from environment variables with sensible
    defaults so the app works out-of-the-box for local development.
    """

    # --- MongoDB ---
    # Connection string. Default: local MongoDB on standard port.
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/api_builder')

    # --- Flask ---
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 'yes')
    PORT = int(os.getenv('FLASK_PORT', 5000))
