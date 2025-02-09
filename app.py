from flask import Flask
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

if __name__ == "__main__":
    app.run(debug=True)
