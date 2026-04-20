from flask import flash, redirect, render_template, session, url_for

from controllers.auth_controller import admin_required
from models.admin_model import (
    delete_user_and_predictions,
    get_admin_dashboard_data,
    toggle_user_status,
)


@admin_required
def admin_panel():
    total_users, total_predictions, successful_logins, failed_logins, users = get_admin_dashboard_data()
    return render_template(
        "pages/admin.html",
        total_users=total_users,
        total_predictions=total_predictions,
        successful_logins=successful_logins,
        failed_logins=failed_logins,
        users=users,
    )


@admin_required
def toggle_user(user_id):
    if user_id == session["user_id"]:
        flash("Cannot deactivate your own account", "danger")
        return redirect(url_for("admin_panel"))
    toggle_user_status(user_id)
    flash("User status updated", "success")
    return redirect(url_for("admin_panel"))


@admin_required
def delete_user(user_id):
    if user_id == session["user_id"]:
        flash("Cannot delete your own account", "danger")
        return redirect(url_for("admin_panel"))
    delete_user_and_predictions(user_id)
    flash("User deleted successfully", "success")
    return redirect(url_for("admin_panel"))
