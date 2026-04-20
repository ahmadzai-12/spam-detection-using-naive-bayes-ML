from datetime import datetime

from flask import flash, jsonify, redirect, render_template, request, session, url_for

from controllers.auth_controller import login_required
from models.prediction_model import (
    delete_all_predictions_for_user,
    get_dashboard_data,
    get_prediction_history,
    save_feedback,
    save_prediction,
)
from models.user_model import get_user_by_id, increment_prediction_count


@login_required
def dashboard():
    user = get_user_by_id(session["user_id"])
    recent_predictions, total, spam_total, avg_confidence = get_dashboard_data(session["user_id"])
    return render_template(
        "pages/dashboard.html",
        user=user,
        total_predictions=total,
        spam_count=spam_total,
        ham_count=total - spam_total,
        avg_confidence=avg_confidence,
        recent_predictions=recent_predictions,
    )


@login_required
def predict(predictor):
    if predictor is None:
        flash("Model not loaded", "danger")
        return redirect(url_for("dashboard"))
    email_text = request.form.get("email_text", "").strip()
    if not email_text:
        flash("Please enter email content", "warning")
        return redirect(url_for("dashboard"))
    try:
        start_time = datetime.now()
        prediction = predictor.predict_email(email_text)
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        prediction_id = save_prediction(
            session["user_id"], email_text, prediction, processing_time, request.remote_addr
        )
        session["last_prediction_id"] = prediction_id
        increment_prediction_count(session["user_id"])
        flash(
            f'Prediction: {prediction["label"]} (Confidence: {prediction["confidence"]:.1f}%)',
            "success",
        )
        return render_template(
            "pages/result.html",
            prediction=prediction,
            email_text=email_text,
            processing_time=f"{processing_time:.2f}ms",
        )
    except Exception as e:
        flash(f"Prediction failed: {str(e)}", "danger")
        return redirect(url_for("dashboard"))


@login_required
def submit_feedback():
    prediction_id = session.get("last_prediction_id")
    if not prediction_id:
        flash("No prediction to provide feedback for", "warning")
        return redirect(url_for("dashboard"))
    correct = request.form.get("correct") == "true"
    actual_label = request.form.get("actual_label") if not correct else None
    comments = request.form.get("comments", "")
    save_feedback(prediction_id, session["user_id"], correct, actual_label, comments)
    flash("Thank you for your feedback! It helps improve our model.", "success")
    return redirect(url_for("dashboard"))


@login_required
def history():
    page = request.args.get("page", 1, type=int)
    per_page = 20
    predictions, total = get_prediction_history(session["user_id"], page, per_page)
    total_pages = (total + per_page - 1) // per_page
    return render_template(
        "pages/history.html",
        predictions=predictions,
        current_page=page,
        total_pages=total_pages,
        total=total,
    )


@login_required
def delete_all_predictions():
    count = delete_all_predictions_for_user(session["user_id"])
    flash(f"All {count} predictions deleted successfully", "success")
    return redirect(url_for("history"))


def api_predict(predictor):
    if predictor is None:
        return jsonify({"error": "Model not loaded"}), 500
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "Missing email field"}), 400
    email_text = data["email"].strip()
    if not email_text:
        return jsonify({"error": "Empty email content"}), 400
    try:
        result = predictor.predict_email(email_text)
        return jsonify({"success": True, "prediction": result, "timestamp": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def health(predictor):
    return jsonify(
        {
            "status": "healthy",
            "model_loaded": predictor is not None,
            "database_connected": True,
            "timestamp": datetime.now().isoformat(),
        }
    )
