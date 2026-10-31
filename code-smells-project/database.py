"""Backward-compatible imports; implementation lives in src.models.database."""

from src.models.database import close_db, configure_database, get_db

__all__ = ["close_db", "configure_database", "get_db"]
