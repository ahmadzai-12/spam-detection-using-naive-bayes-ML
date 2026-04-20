import os

from flask import Flask

from predict import SpamPredictor
from models.setup_model import init_db
from routes import init_routes


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your-super-secret-key-change-this-in-production-2024"
    app.config["DATABASE"] = "spam_detection.db"

    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)

    try:
        predictor = SpamPredictor("models/spam_model.pkl")
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        predictor = None

    with app.app_context():
        init_db()
        print("Database initialized successfully!")

    init_routes(app, predictor)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
