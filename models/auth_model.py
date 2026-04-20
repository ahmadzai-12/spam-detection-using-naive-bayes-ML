import hashlib
import re
import secrets
from datetime import datetime

from .db import get_connection


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"


def log_login_attempt(user_id, ip_address, user_agent, success):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO login_history (user_id, ip_address, user_agent, success) VALUES (?, ?, ?, ?)",
        (user_id, ip_address, user_agent, success),
    )
    conn.commit()
    conn.close()


def create_password_reset(email):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    token = None

    if user:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now().replace(hour=23, minute=59, second=59)
        c.execute(
            "INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user[0], token, expires_at),
        )
        conn.commit()

    conn.close()
    return user, token


def get_valid_reset_token(token):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT user_id, expires_at, used FROM password_resets WHERE token = ?",
        (token,),
    )
    reset = c.fetchone()
    conn.close()
    return reset


def reset_user_password(token, user_id, new_password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE id = ?", (hash_password(new_password), user_id))
    c.execute("UPDATE password_resets SET used = 1 WHERE token = ?", (token,))
    conn.commit()
    conn.close()
