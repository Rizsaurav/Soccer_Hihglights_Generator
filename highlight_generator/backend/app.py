import os
import sys
from flask import Flask, request
from flask_cors import CORS

# === Ensure project root is in Python path ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# === Import blueprint after fixing path ===
from routes.upload import upload_bp 
app = Flask(__name__)

# === Enable CORS globally for development (adjust origins in prod) ===
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

# === Register route blueprints ===
app.register_blueprint(upload_bp)

# === Optional: Base health check ===
@app.route("/")
def index():
    return {"status": "Highlight Generator API is running."}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
