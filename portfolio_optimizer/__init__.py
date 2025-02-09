from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["portfolio_optimizer"]

# Users Collection Schema
users_collection = db["users"]
portfolios_collection = db["portfolios"]
goals_collection = db["goals"]
market_data_collection = db["market_data"]

# Example Schema Definitions (Documents)

# Users Schema
sample_user = {
    "name": "John Doe",
    "email": "johndoe@example.com",
    "password_hash": "hashed_password_here",  # Will use hashing later
    "created_at": "2025-01-29"
}

# Portfolios Schema
sample_portfolio = {
    "user_email": "johndoe@example.com",
    "assets": [
        {"ticker": "AAPL", "quantity": 10, "purchase_price": 150},
        {"ticker": "TSLA", "quantity": 5, "purchase_price": 700}
    ],
    "created_at": "2025-01-29"
}

# Goals Schema
sample_goal = {
    "user_email": "johndoe@example.com",
    "goal_name": "Retirement Fund",
    "target_amount": 500000,
    "current_progress": 10000,
    "deadline": "2040-01-01",
    "created_at": "2025-01-29"
}

# Market Data Schema
sample_market_data = {
    "ticker": "AAPL",
    "price": 175,
    "date": "2025-01-29",
    "open": 170,
    "high": 180,
    "low": 168,
    "volume": 5000000
}