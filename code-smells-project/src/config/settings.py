import os


def load_settings():
    """Load secrets and runtime settings from the process environment."""
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY must be set in the environment")

    return {
        "SECRET_KEY": secret_key,
        "ADMIN_TOKEN": os.environ.get("ADMIN_TOKEN"),
        "DEBUG": os.environ.get("FLASK_DEBUG", "true").lower() == "true",
        "DATABASE_PATH": os.environ.get("DATABASE_PATH", "loja.db"),
    }
