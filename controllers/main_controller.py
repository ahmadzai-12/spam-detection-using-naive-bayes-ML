from flask import redirect, render_template, session, url_for


def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("pages/index.html")


def not_found_error(error):
    return render_template("errors/404.html"), 404


def internal_error(error):
    return render_template("errors/500.html"), 500
