from .admin_routes import init_admin_routes
from .auth_routes import init_auth_routes
from .main_routes import init_main_routes
from .prediction_routes import init_prediction_routes


def init_routes(app, predictor):
    init_main_routes(app)
    init_auth_routes(app)
    init_prediction_routes(app, predictor)
    init_admin_routes(app)
