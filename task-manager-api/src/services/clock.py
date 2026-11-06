from datetime import datetime, timezone


def utc_now():
    """Return naive UTC for compatibility with the existing SQLite columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
