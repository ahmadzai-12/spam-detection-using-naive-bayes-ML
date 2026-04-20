from controllers.auth_controller import (
    change_password,
    edit_profile,
    forgot_password,
    login,
    logout,
    profile,
    register,
    reset_password,
)


def init_auth_routes(app):
    app.add_url_rule("/login", endpoint="login", view_func=login, methods=["GET", "POST"])
    app.add_url_rule("/register", endpoint="register", view_func=register, methods=["GET", "POST"])
    app.add_url_rule("/logout", endpoint="logout", view_func=logout)
    app.add_url_rule("/profile", endpoint="profile", view_func=profile)
    app.add_url_rule("/profile/edit", endpoint="edit_profile", view_func=edit_profile, methods=["GET", "POST"])
    app.add_url_rule(
        "/change-password",
        endpoint="change_password",
        view_func=change_password,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/forgot-password",
        endpoint="forgot_password",
        view_func=forgot_password,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/reset-password/<token>",
        endpoint="reset_password",
        view_func=reset_password,
        methods=["GET", "POST"],
    )
