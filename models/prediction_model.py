from .db import get_connection


def get_profile_stats(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ?", (user_id,))
    total_predictions = c.fetchone()[0]
    c.execute(
        "SELECT prediction, COUNT(*) FROM predictions WHERE user_id = ? GROUP BY prediction",
        (user_id,),
    )
    prediction_stats = dict(c.fetchall())
    c.execute(
        "SELECT login_time, ip_address, success FROM login_history WHERE user_id = ? ORDER BY login_time DESC LIMIT 5",
        (user_id,),
    )
    login_history = c.fetchall()
    conn.close()
    return total_predictions, prediction_stats, login_history


def get_dashboard_data(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """SELECT id, email_text, prediction, confidence, created_at
           FROM predictions
           WHERE user_id = ?
           ORDER BY created_at DESC
           LIMIT 10""",
        (user_id,),
    )
    recent_predictions = c.fetchall()
    c.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ?", (user_id,))
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ? AND prediction = 'Spam'", (user_id,))
    spam_total = c.fetchone()[0]
    c.execute("SELECT AVG(confidence) FROM predictions WHERE user_id = ?", (user_id,))
    avg_confidence = c.fetchone()[0] or 0
    conn.close()
    return recent_predictions, total, spam_total, avg_confidence


def save_prediction(user_id, email_text, prediction, processing_time, ip_address):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO predictions
           (user_id, email_text, prediction, spam_probability, ham_probability,
            confidence, processing_time, ip_address)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            user_id,
            email_text[:500],
            prediction["label"],
            prediction["spam_probability"],
            prediction["ham_probability"],
            prediction["confidence"],
            processing_time,
            ip_address,
        ),
    )
    prediction_id = c.lastrowid
    conn.commit()
    conn.close()
    return prediction_id


def save_feedback(prediction_id, user_id, correct, actual_label, comments):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO feedback (prediction_id, user_id, correct, actual_label, comments)
           VALUES (?, ?, ?, ?, ?)""",
        (prediction_id, user_id, correct, actual_label, comments),
    )
    conn.commit()
    conn.close()


def get_prediction_history(user_id, page, per_page):
    offset = (page - 1) * per_page
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ?", (user_id,))
    total = c.fetchone()[0]
    c.execute(
        """SELECT id, email_text, prediction, confidence, created_at
           FROM predictions
           WHERE user_id = ?
           ORDER BY created_at DESC
           LIMIT ? OFFSET ?""",
        (user_id, per_page, offset),
    )
    predictions = c.fetchall()
    conn.close()
    return predictions, total


def delete_all_predictions_for_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ?", (user_id,))
    count = c.fetchone()[0]
    c.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
    c.execute("UPDATE users SET predictions_count = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return count
