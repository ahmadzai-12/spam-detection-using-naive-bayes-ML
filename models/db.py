import sqlite3
from flask import current_app


def get_connection():
    """Return a SQLite connection for the configured database."""
    return sqlite3.connect(current_app.config["DATABASE"])
