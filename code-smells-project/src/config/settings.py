import os
import secrets
from pathlib import Path


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(Path.cwd() / "loja.db"))
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


def validate_settings(settings=Settings):
    return settings
