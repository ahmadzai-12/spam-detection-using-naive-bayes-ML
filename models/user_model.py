from .db import get_connection
from .auth_model import hash_password


def get_user_for_login(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, username, email, password, is_admin, role, is_active FROM users WHERE username = ?",
        (username,),
    )
    user = c.fetchone()
    conn.close()
    return user


def create_user(username, email, full_name, password, role="user"):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, email, password, full_name, role) VALUES (?, ?, ?, ?, ?)",
        (username, email, hash_password(password), full_name, role),
    )
    conn.commit()
    conn.close()


def username_or_email_exists(username, email):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
    existing = c.fetchone()
    conn.close()
    return existing is not None


def get_user_by_id(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, username, email, full_name, created_at, last_login, is_admin, role, predictions_count FROM users WHERE id = ?",
        (user_id,),
    )
    user = c.fetchone()
    conn.close()
    return user


def update_last_login(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def update_profile(user_id, full_name, email):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET full_name = ?, email = ? WHERE id = ?", (full_name, email, user_id))
    conn.commit()
    conn.close()


def get_password_hash(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def set_password(user_id, new_password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE id = ?", (hash_password(new_password), user_id))
    conn.commit()
    conn.close()


def increment_prediction_count(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET predictions_count = predictions_count + 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
