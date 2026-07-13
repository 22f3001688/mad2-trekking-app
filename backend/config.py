import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"

load_dotenv(BASE_DIR / ".env")


def _resolve_database_uri():
    configured_uri = os.getenv("DATABASE_URI") or os.getenv("DATABASE_URL")
    default_uri = f"sqlite:///{(INSTANCE_DIR / 'trekscape.db').as_posix()}"

    if not configured_uri:
        return default_uri

    if configured_uri.startswith("sqlite:///"):
        database_path = configured_uri.replace("sqlite:///", "", 1)
        if not os.path.isabs(database_path):
            database_path = str((BASE_DIR / database_path).resolve())
            return f"sqlite:///{database_path}"
        return configured_uri

    return configured_uri


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = _resolve_database_uri()

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret")

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    CELERY_TIMEZONE = os.getenv("CELERY_TIMEZONE", "Asia/Kolkata")
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/2")
    TREK_CACHE_TTL = int(os.getenv("TREK_CACHE_TTL", "300"))

    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "1025"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "false").strip().lower() in {"1", "true", "yes", "on"}
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "trekscape@example.com")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@trekscape.com")