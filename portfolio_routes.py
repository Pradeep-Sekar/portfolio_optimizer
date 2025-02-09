from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
from datetime import datetime

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["portfolio_optimizer"]

portfolio_api = Blueprint('portfolio_api', __name__)

@portfolio_api.route("/add_to_portfolio", methods=["POST"])
@jwt_required()
def add_to_portfolio():
    try:
        user_email = get_jwt_identity()
        data = request.json

        portfolio_entry = {
            "user_email": user_email,
            "ticker": data.get("ticker"),
            "quantity": data.get("quantity"),
            "average_price": data.get("average_price"),
            "investment_date": data.get("investment_date"),
            "created_at": datetime.utcnow()
        }

        db.portfolios.insert_one(portfolio_entry)
        return jsonify({"message": "Stock added to portfolio successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@portfolio_api.route("/portfolio", methods=["GET"])
@jwt_required()
def get_portfolio():
    try:
        user_email = get_jwt_identity()
        user_portfolio = list(db.portfolios.find({"user_email": user_email}, {"_id": 0}))

        return jsonify(user_portfolio)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
