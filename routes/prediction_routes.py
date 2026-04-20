from controllers.prediction_controller import (
    api_predict,
    dashboard,
    delete_all_predictions,
    health,
    history,
    predict,
    submit_feedback,
)


def init_prediction_routes(app, predictor):
    app.add_url_rule("/dashboard", endpoint="dashboard", view_func=dashboard)
    app.add_url_rule(
        "/predict",
        endpoint="predict",
        view_func=lambda: predict(predictor),
        methods=["POST"],
    )
    app.add_url_rule(
        "/submit-feedback",
        endpoint="submit_feedback",
        view_func=submit_feedback,
        methods=["POST"],
    )
    app.add_url_rule("/history", endpoint="history", view_func=history)
    app.add_url_rule(
        "/delete-all-predictions",
        endpoint="delete_all_predictions",
        view_func=delete_all_predictions,
        methods=["POST"],
    )
    app.add_url_rule(
        "/api/predict",
        endpoint="api_predict",
        view_func=lambda: api_predict(predictor),
        methods=["POST"],
    )
    app.add_url_rule("/health", endpoint="health", view_func=lambda: health(predictor))
