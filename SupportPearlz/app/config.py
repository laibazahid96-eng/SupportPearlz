"""
Application configuration.

Settings are read from environment variables so that no secrets ever need
to be committed to source control. Copy `.env.example` to `.env` and fill
in real values for local development.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Base configuration shared by all environments."""

    # Flask signs session cookies with this key. In production this MUST
    # be set via the SECRET_KEY environment variable to a long random
    # value (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`).
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-me")

    # Server-side session storage so the customer's OpenAI API key never
    # travels to the browser inside a cookie.
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = str(BASE_DIR / "instance" / "flask_session")
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

    # Cookie hardening.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"

    # Knowledge base + OpenAI settings.
    KNOWLEDGE_BASE_PATH = os.environ.get(
        "KNOWLEDGE_BASE_PATH", str(BASE_DIR / "data" / "knowledge.txt")
    )
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TIMEOUT_SECONDS = float(os.environ.get("OPENAI_TIMEOUT_SECONDS", "20"))

    # Simple abuse protection on the chat endpoint.
    RATELIMIT_CHAT = os.environ.get("RATELIMIT_CHAT", "10 per minute")

    MAX_QUESTION_LENGTH = 800


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SESSION_FILE_DIR = str(BASE_DIR / "instance" / "flask_session_test")


CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
