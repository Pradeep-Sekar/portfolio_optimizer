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

        new_asset = {
            "ticker": data.get("ticker"),
            "quantity": data.get("quantity"),
            "average_price": data.get("average_price"),
            "investment_date": data.get("investment_date")
        }

        existing_portfolio = db.portfolios.find_one({"user_email": user_email})

        if existing_portfolio:
            # Check if stock already exists in portfolio
            asset_exists = any(asset["ticker"] == new_asset["ticker"] for asset in existing_portfolio.get("assets", []))

            if asset_exists:
                return jsonify({"message": "Stock already exists in portfolio!"}), 400
            
            # Push new stock into the assets array
            db.portfolios.update_one(
                {"user_email": user_email},
                {"$push": {"assets": new_asset}}
            )
        else:
            # Create a new portfolio entry
            portfolio_entry = {
                "user_email": user_email,
                "assets": [new_asset],
                "created_at": datetime.utcnow()
            }
            db.portfolios.insert_one(portfolio_entry)

        return jsonify({"message": f"Stock {new_asset['ticker']} added successfully for {user_email}!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@portfolio_api.route("/portfolio", methods=["GET"])
@jwt_required()
def get_portfolio():
    try:
        user_email = get_jwt_identity()
        user_portfolio = db.portfolios.find_one({"user_email": user_email}, {"_id": 0})

        if not user_portfolio:
            return jsonify({"message": "No portfolio found for this user."}), 404

        return jsonify(user_portfolio)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
