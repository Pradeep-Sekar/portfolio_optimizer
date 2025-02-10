from pymongo import MongoClient
import os

# Get MongoDB connection string from environment variable or use default
mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/portfolio_optimizer")

# Create MongoDB client
client = MongoClient(mongo_uri)

# Get database instance
db = client.get_database()
