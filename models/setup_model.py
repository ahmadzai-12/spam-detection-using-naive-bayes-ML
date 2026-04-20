from .db import get_connection
from .auth_model import hash_password


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            is_admin INTEGER DEFAULT 0,
            predictions_count INTEGER DEFAULT 0,
            role TEXT DEFAULT 'user'
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            email_text TEXT,
            cleaned_text TEXT,
            prediction TEXT,
            spam_probability REAL,
            ham_probability REAL,
            confidence REAL,
            processing_time REAL,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            token TEXT UNIQUE,
            expires_at TIMESTAMP,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ip_address TEXT,
            user_agent TEXT,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id INTEGER,
            user_id INTEGER,
            correct BOOLEAN,
            actual_label TEXT,
            comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (prediction_id) REFERENCES predictions (id)
        )"""
    )
    try:
        c.execute(
            "INSERT INTO users (username, email, password, full_name, is_admin, role) VALUES (?, ?, ?, ?, ?, ?)",
            (
                "admin",
                "admin@spamdetector.com",
                hash_password("Admin@123"),
                "System Administrator",
                1,
                "admin",
            ),
        )
    except Exception:
        pass
    try:
        c.execute(
            "INSERT INTO users (username, email, password, full_name, role) VALUES (?, ?, ?, ?, ?)",
            ("demo", "demo@example.com", hash_password("Demo@123"), "Demo User", "user"),
        )
    except Exception:
        pass
    conn.commit()
    conn.close()
