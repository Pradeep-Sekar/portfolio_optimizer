from flask import Blueprint, jsonify, request, session
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
    
    print(f"Login attempt for email: {email}")

    if not email or not password:
        print("Login failed: Missing email or password")
        return jsonify({"status": "error", "message": "Email and password are required"}), 400

    user = db.users.find_one({"email": email})
    if not user:
        print(f"Login failed: No user found with email {email}")
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401
    
    print(f"User found, verifying password for {email}")
    if not check_password_hash(user["password_hash"], password):
        print(f"Login failed: Invalid password for {email}")
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    print(f"Login successful for {email}")
    # Store user email in session and generate JWT token
    session["user_email"] = email
    access_token = create_access_token(identity=email)
    return jsonify({
        "status": "success",
        "message": "Login successful",
        "data": {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 86400  # 24 hours in seconds
        }
    })

# Protected Route (Requires JWT)
@user_api.route("/get_users", methods=["GET"])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()
    users = list(db.users.find({}, {"_id": 0, "password_hash": 0}))  # Exclude password
    return jsonify({"current_user": current_user, "users": users})
