from controllers.main_controller import home, internal_error, not_found_error


def init_main_routes(app):
    app.add_url_rule("/", endpoint="home", view_func=home)
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_error)
