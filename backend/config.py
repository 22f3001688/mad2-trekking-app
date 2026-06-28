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