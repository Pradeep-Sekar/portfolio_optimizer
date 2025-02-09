from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import yfinance as yf
from pymongo import MongoClient
from portfolio_routes import portfolio_api
from user_routes import user_api
from goal_routes import goal_api

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["portfolio_optimizer"]

api = Blueprint('api', __name__)

@api.route("/")
def home():
    return "Welcome to the Portfolio Optimizer API!"

# List of known Indian tickers (can be expanded dynamically later)
known_nse_tickers = {"RELIANCE", "TCS", "INFY", "HDFC", "ICICIBANK", "KOTAKBANK", "SBIN", "ITC"}
@api.route("/stock/<ticker>", methods=["GET"])
def get_stock_price(ticker):
    try:
        ticker = ticker.upper()

        # Add .NS for known Indian tickers
        if not ticker.endswith(".NS") and not ticker.endswith(".BO"):
            if ticker in known_nse_tickers:
                ticker += ".NS"
            else:
                ticker += ""

        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")

        if data.empty:
            return jsonify({"error": "Invalid ticker or no data available"}), 404

        # Prepare stock info
        stock_info = {
            "ticker": ticker,
            "price": round(data["Close"].iloc[-1], 2),
            "date": data.index[-1].to_pydatetime(),  # Use ISODate (datetime format)
            "open": round(data["Open"].iloc[-1], 2),
            "high": round(data["High"].iloc[-1], 2),
            "low": round(data["Low"].iloc[-1], 2),
            "volume": int(data["Volume"].iloc[-1]),
        }

        # Save to MongoDB (upsert to prevent duplicates)
        db.market_data.update_one(
            {"ticker": stock_info["ticker"], "date": stock_info["date"]},  # Match on ticker and date
            {"$set": stock_info},  # Update or insert
            upsert=True
        )

        return jsonify(stock_info)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@api.route("/market_data", methods=["GET"])
def get_market_data():
    try:
        # Fetch all market data, exclude MongoDB `_id` field for cleaner output
        data = list(db.market_data.find({}, {"_id": 0}))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Register the user, portfolio, and goal blueprints
api.register_blueprint(user_api, url_prefix='/user')
api.register_blueprint(portfolio_api, url_prefix='/portfolio')
api.register_blueprint(goal_api, url_prefix='/goal')
