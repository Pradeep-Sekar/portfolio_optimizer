from flask import Flask, render_template, redirect, url_for, session, request
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
from routes import api

app = Flask(__name__)

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "supersecretkey")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)  # Token expires in 1 hour
jwt = JWTManager(app)

# Register the API blueprint
app.register_blueprint(api)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Simulate login process
        user_email = request.form.get("email")
        session["user_email"] = user_email
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    user_email = session.get("user_email")
    if not user_email:
        return redirect(url_for("login"))

    # Fetch portfolio data
    portfolio_data = fetch_portfolio_data(user_email)
    return render_template("dashboard.html", portfolio=portfolio_data)

def fetch_portfolio_data(user_email):
    # Simulate fetching portfolio data from /portfolio/track
    # This should be replaced with actual API call logic
    return {
        "user_email": user_email,
        "portfolio_value": 10000,
        "assets": [
            {"ticker": "AAPL", "quantity": 10, "purchase_price": 150, "current_price": 170},
            {"ticker": "GOOGL", "quantity": 5, "purchase_price": 1000, "current_price": 1100}
        ]
    }
    app.run(debug=True)
