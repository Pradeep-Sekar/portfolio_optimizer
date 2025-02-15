from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
from datetime import datetime

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["portfolio_optimizer"]

goal_api = Blueprint('goal_api', __name__)

@goal_api.route("/add_goal", methods=["POST"])
@jwt_required()
def add_goal():
    try:
        user_email = get_jwt_identity()  # Get logged-in user
        data = request.json

        goal = {
            "user_email": user_email,
            "goal_name": data.get("goal_name"),
            "target_amount": data.get("target_amount"),
            "current_progress": data.get("current_progress", 0),  # Default: 0
            "deadline": data.get("deadline"),
            "created_at": datetime.utcnow()
        }

        db.goals.insert_one(goal)
        return jsonify({"message": "Goal added successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@goal_api.route("/goals", methods=["GET"])
@jwt_required()
def get_goals():
    try:
        user_email = get_jwt_identity()
        user_goals = list(db.goals.find({"user_email": user_email}, {"_id": 0}))
        return jsonify(user_goals)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@goal_api.route("/goal_progress", methods=["GET"])
@jwt_required()
def goal_progress():
    try:
        user_email = get_jwt_identity()

        # Fetch all goals for the logged-in user
        user_goals = list(db.goals.find({"user_email": user_email}, {"_id": 0}))

        if not user_goals:
            return jsonify({"message": "No goals found for this user"}), 404

        progress_report = []

        for goal in user_goals:
            target = goal["target_amount"]
            current = goal["current_progress"]
            deadline = datetime.strptime(goal["deadline"], "%Y-%m-%d")

            # Calculate progress percentage
            progress_percentage = round((current / target) * 100, 2)

            # Calculate time left in years & months
            today = datetime.utcnow()
            time_left = (deadline - today).days / 365  # Convert days to years
            if time_left <= 0:
                time_left = 0.01  # Prevent division by zero if deadline is near

            # Calculate suggested monthly investment to stay on track
            amount_needed = target - current
            months_left = time_left * 12
            monthly_investment_needed = round(amount_needed / months_left, 2)

            progress_report.append({
                "goal_name": goal["goal_name"],
                "target_amount": target,
                "current_progress": current,
                "progress_percentage": progress_percentage,
                "deadline": goal["deadline"],
                "years_left": round(time_left, 2),
                "monthly_investment_needed": monthly_investment_needed
            })

        return jsonify(progress_report)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@goal_api.route("/investment_suggestions", methods=["GET"])
@jwt_required()
def investment_suggestions():
    try:
        user_email = get_jwt_identity()

        # Fetch user goals
        user_goals = list(db.goals.find({"user_email": user_email}, {"_id": 0}))

        if not user_goals:
            return jsonify({"message": "No goals found for this user"}), 404

        suggestions = []

        for goal in user_goals:
            target = goal["target_amount"]
            current = goal["current_progress"]
            deadline = datetime.strptime(goal["deadline"], "%Y-%m-%d")

            # Calculate progress and time left
            progress_percentage = round((current / target) * 100, 2)
            today = datetime.utcnow()
            time_left_years = (deadline - today).days / 365
            if time_left_years <= 0:
                time_left_years = 0.01  # Prevent division by zero

            amount_needed = target - current
            monthly_investment_needed = round(amount_needed / (time_left_years * 12), 2)

            # Fetch market data for analysis
            stock_ticker = "NSEI"  # Can change based on user preference
            stock = yf.Ticker(stock_ticker)
            data = stock.history(period="5y")  # Get last 5 years of data

            if data.empty:
                market_growth_rate = 0.07  # Assume 7% annual growth if data is unavailable
            else:
                start_price = data["Close"].iloc[0]
                end_price = data["Close"].iloc[-1]
                years = 5
                market_growth_rate = ((end_price / start_price) ** (1/years)) - 1

            # Calculate market growth rate (CAGR)
            start_price = data["Close"].iloc[0]
            end_price = data["Close"].iloc[-1]
            years = 5
            market_growth_rate = ((end_price / start_price) ** (1/years)) - 1

            # Adjust investment strategy based on market trends
            if progress_percentage < 50:
                suggested_strategy = "Increase investments. Consider high-growth stocks or ETFs."
            elif market_growth_rate > 0.08:  # 8% annual return
                suggested_strategy = "Stock market is performing well. Stay invested in equities."
            else:
                suggested_strategy = "Market is volatile. Consider balanced funds or SIP investments."

            suggestions.append({
                "goal_name": goal["goal_name"],
                "target_amount": target,
                "current_progress": current,
                "progress_percentage": progress_percentage,
                "deadline": goal["deadline"],
                "years_left": round(time_left_years, 2),
                "monthly_investment_needed": monthly_investment_needed,
                "suggested_strategy": suggested_strategy
            })

        return jsonify(suggestions)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
