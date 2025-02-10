from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
from datetime import datetime, date

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

@portfolio_api.route("/history", methods=["GET"])
@jwt_required()
def get_portfolio_history():
    try:
        user_email = get_jwt_identity()
        days = int(request.args.get("days", 30))  # Default to last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Fetch portfolio history within the specified date range
        portfolio_history = list(db.portfolio_history.find(
            {
                "user_email": user_email,
                "date": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}
            },
            {"_id": 0}
        ).sort("date", -1))  # Sort by date descending (most recent first)

        # Calculate percentage change compared to the previous day
        for i in range(1, len(portfolio_history)):
            previous_value = portfolio_history[i]["portfolio_value"]
            current_value = portfolio_history[i - 1]["portfolio_value"]
            percentage_change = ((current_value - previous_value) / previous_value) * 100
            portfolio_history[i - 1]["percentage_change"] = round(percentage_change, 2)

        return jsonify(portfolio_history)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

import numpy as np
from portfolio_optimizer.optimizer import PortfolioOptimizer

@portfolio_api.route("/track", methods=["GET"])
@jwt_required()
def track_portfolio():
    """
    Fetch real-time stock prices and compute portfolio performance.
    :return: JSON response with portfolio valuation.
    """
    try:
        user_email = get_jwt_identity()
        user_portfolio = db.portfolios.find_one({"user_email": user_email}, {"_id": 0})

        if not user_portfolio:
            return jsonify({"message": "No portfolio found for this user."}), 404

        assets = [asset["ticker"] for asset in user_portfolio["assets"]]
        holdings = {asset["ticker"]: (asset["quantity"], asset["purchase_price"]) for asset in user_portfolio["assets"]}

        optimizer = PortfolioOptimizer(assets, returns=np.zeros(len(assets)), cov_matrix=np.zeros((len(assets), len(assets))))
        
        # Get live prices
        live_prices = optimizer.get_live_prices()

        portfolio_value = 0
        asset_values = {}
        
        # Prepare asset values for history
        assets_for_history = []

        for ticker, (quantity, purchase_price) in holdings.items():
            current_price = live_prices.get(ticker, None)

            if current_price is not None:
                current_value = quantity * current_price
                profit_loss = current_value - (quantity * purchase_price)
                percentage_change = ((profit_loss) / (quantity * purchase_price)) * 100

                asset_values[ticker] = {
                    "quantity": quantity,
                    "purchase_price": purchase_price,
                    "current_price": round(current_price, 2),
                    "current_value": round(current_value, 2),
                    "profit_loss": round(profit_loss, 2),
                    "percentage_change": round(percentage_change, 2)
                }
                portfolio_value += current_value
                
                assets_for_history.append({
                    "ticker": ticker,
                    "quantity": quantity,
                    "purchase_price": purchase_price,
                    "current_price": round(current_price, 2)
                })
            else:
                asset_values[ticker] = {
                    "quantity": quantity,
                    "purchase_price": purchase_price,
                    "current_price": "N/A",
                    "current_value": "N/A",
                    "profit_loss": "N/A",
                    "percentage_change": "N/A"
                }

        # Save daily snapshot of portfolio history
        today = date.today().isoformat()
        existing_snapshot = db.portfolio_history.find_one({
            "user_email": user_email,
            "date": today
        })

        if not existing_snapshot:
            snapshot = {
                "user_email": user_email,
                "date": today,
                "portfolio_value": round(portfolio_value, 2),
                "assets": [
                    {
                        "ticker": asset["ticker"],
                        "quantity": asset["quantity"],
                        "purchase_price": asset["purchase_price"],
                        "current_price": asset["current_price"]
                    }
                    for asset in assets_for_history
                ]
            }
            db.portfolio_history.insert_one(snapshot)

        return jsonify({
            "portfolio_value": round(portfolio_value, 2),
            "assets": asset_values
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
