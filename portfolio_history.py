from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from datetime import datetime

portfolio_history_api = Blueprint("portfolio_history_api", __name__)

@portfolio_history_api.route("/history/save", methods=["POST"])
@jwt_required()
def save_portfolio_history():
    """Save a snapshot of the user's portfolio."""
    try:
        user_email = get_jwt_identity()
        data = request.json  # Expecting portfolio_value and assets

        snapshot = {
            "user_email": user_email,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "portfolio_value": data.get("portfolio_value", 0),
            "assets": data.get("assets", []),
            "created_at": datetime.utcnow(),
        }

        db.portfolio_history.insert_one(snapshot)
        return jsonify({"message": "Portfolio history saved successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@portfolio_history_api.route("/history", methods=["GET"])
@jwt_required()
def get_portfolio_history():
    """Fetch historical portfolio data."""
    try:
        user_email = get_jwt_identity()
        history = list(db.portfolio_history.find({"user_email": user_email}, {"_id": 0}))

        return jsonify({"data": history, "status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
