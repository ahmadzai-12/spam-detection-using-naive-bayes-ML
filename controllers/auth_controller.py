import re
from datetime import datetime
from functools import wraps

from flask import flash, redirect, render_template, request, session, url_for

from models.auth_model import (
    create_password_reset,
    get_valid_reset_token,
    hash_password,
    log_login_attempt,
    reset_user_password,
    validate_email,
    validate_password,
)
from models.prediction_model import get_profile_stats
from models.user_model import (
    create_user,
    get_password_hash,
    get_user_by_id,
    get_user_for_login,
    set_password,
    update_last_login,
    update_profile,
    username_or_email_exists,
)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to access this page", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first", "warning")
            return redirect(url_for("login"))
        if not session.get("is_admin"):
            flash("Admin access required", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)

    return decorated


def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember", False)
        if not username or not password:
            flash("Please enter both username and password", "danger")
            return render_template("pages/login.html")
        user = get_user_for_login(username)
        if user and user[3] == hash_password(password):
            if user[6] == 0:
                flash("Your account has been deactivated. Contact administrator.", "danger")
                return render_template("pages/login.html")
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["user_email"] = user[2]
            session["is_admin"] = user[4]
            session["role"] = user[5]
            if remember:
                session.permanent = True
            update_last_login(user[0])
            log_login_attempt(user[0], request.remote_addr, request.headers.get("User-Agent"), 1)
            flash(f"Welcome back, {user[1]}!", "success")
            return redirect(url_for("dashboard"))
        log_login_attempt(None, request.remote_addr, request.headers.get("User-Agent"), 0)
        flash("Invalid username or password", "danger")
    return render_template("pages/login.html")


def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        full_name = request.form.get("full_name", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        errors = []
        if not username:
            errors.append("Username is required")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters")
        elif not re.match(r"^[a-zA-Z0-9_]+$", username):
            errors.append("Username can only contain letters, numbers and underscore")
        if not email:
            errors.append("Email is required")
        elif not validate_email(email):
            errors.append("Invalid email format")
        if not password:
            errors.append("Password is required")
        else:
            is_valid, msg = validate_password(password)
            if not is_valid:
                errors.append(msg)
        if password != confirm_password:
            errors.append("Passwords do not match")
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("pages/register.html", username=username, email=email, full_name=full_name)
        if username_or_email_exists(username, email):
            flash("Username or email already exists", "danger")
            return render_template("pages/register.html", username=username, email=email, full_name=full_name)
        try:
            create_user(username, email, full_name, password)
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Registration failed: {str(e)}", "danger")
    return render_template("pages/register.html")


def logout():
    username = session.get("username", "User")
    session.clear()
    flash(f"Goodbye, {username}! You have been logged out.", "info")
    return redirect(url_for("home"))


@login_required
def profile():
    user = get_user_by_id(session["user_id"])
    total_predictions, prediction_stats, login_history = get_profile_stats(session["user_id"])
    return render_template(
        "pages/profile.html",
        user=user,
        total_predictions=total_predictions,
        spam_count=prediction_stats.get("Spam", 0),
        ham_count=prediction_stats.get("Ham", 0),
        login_history=login_history,
    )


@login_required
def edit_profile():
    if request.method == "POST":
        full_name = request.form.get("full_name", "")
        email = request.form.get("email", "")
        if email and not validate_email(email):
            flash("Invalid email format", "danger")
            return redirect(url_for("edit_profile"))
        update_profile(session["user_id"], full_name, email)
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))
    user = get_user_by_id(session["user_id"])
    return render_template("pages/edit-profile.html", user=user)


@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        if hash_password(current_password) != get_password_hash(session["user_id"]):
            flash("Current password is incorrect", "danger")
            return redirect(url_for("change_password"))
        is_valid, msg = validate_password(new_password)
        if not is_valid:
            flash(msg, "danger")
            return redirect(url_for("change_password"))
        if new_password != confirm_password:
            flash("New passwords do not match", "danger")
            return redirect(url_for("change_password"))
        set_password(session["user_id"], new_password)
        flash("Password changed successfully!", "success")
        return redirect(url_for("profile"))
    return render_template("pages/change-password.html")


def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "")
        user, token = create_password_reset(email)
        if user:
            flash(f"Password reset link sent to {email}. Use token: {token}", "info")
        else:
            flash("Email not found", "danger")
    return render_template("pages/forgot-password.html")


def reset_password(token):
    reset = get_valid_reset_token(token)
    if not reset or reset[2] == 1 or datetime.now() > datetime.strptime(reset[1], "%Y-%m-%d %H:%M:%S"):
        flash("Invalid or expired reset token", "danger")
        return redirect(url_for("login"))
    if request.method == "POST":
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        is_valid, msg = validate_password(new_password)
        if not is_valid:
            flash(msg, "danger")
            return render_template("pages/reset-password.html", token=token)
        if new_password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template("pages/reset-password.html", token=token)
        reset_user_password(token, reset[0], new_password)
        flash("Password reset successful! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("pages/reset-password.html", token=token)
