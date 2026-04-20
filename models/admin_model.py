from .db import get_connection


def get_admin_dashboard_data():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM login_history WHERE success = 1")
    successful_logins = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM login_history WHERE success = 0")
    failed_logins = c.fetchone()[0]
    c.execute(
        "SELECT id, username, email, full_name, created_at, last_login, is_active, role, predictions_count FROM users ORDER BY created_at DESC"
    )
    users = c.fetchall()
    conn.close()
    return total_users, total_predictions, successful_logins, failed_logins, users


def toggle_user_status(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_active = NOT is_active WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def delete_user_and_predictions(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    c.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
