from controllers.admin_controller import admin_panel, delete_user, toggle_user


def init_admin_routes(app):
    app.add_url_rule("/admin", endpoint="admin_panel", view_func=admin_panel)
    app.add_url_rule("/admin/toggle-user/<int:user_id>", endpoint="toggle_user", view_func=toggle_user)
    app.add_url_rule("/admin/delete-user/<int:user_id>", endpoint="delete_user", view_func=delete_user)
