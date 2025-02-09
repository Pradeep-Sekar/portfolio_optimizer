from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["portfolio_optimizer"]

user_api = Blueprint('user_api', __name__)

# User Registration Route
@user_api.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Check if user already exists
    if db.users.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    # Hash the password and store user
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)
    user = {
        "email": email,
        "password_hash": hashed_password,
        "created_at": datetime.utcnow()
    }
    db.users.insert_one(user)

    return jsonify({"message": "User registered successfully!"}), 201

# User Login Route (JWT Token Generation)
@user_api.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = db.users.find_one({"email": email})
    
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Generate JWT token
    access_token = create_access_token(identity=email)
    return jsonify({"access_token": access_token})

# Protected Route (Requires JWT)
@user_api.route("/get_users", methods=["GET"])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()
    users = list(db.users.find({}, {"_id": 0, "password_hash": 0}))  # Exclude password
    return jsonify({"current_user": current_user, "users": users})
