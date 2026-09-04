from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
  return "<h1>Hello, World!</h1>"

@app.route("/health", methods=['GET'])
def get_health():
  database_up = os.getenv("DB_STATUS", "up") == "up"

  health_response = {
    "status": "healthy",
    "checks": {
      "database": "up"
    }
  }

  if not database_up:
    health_response["status"] = "unhealthy"
    health_response["checks"]["database"] = "down"
  
  return jsonify(health_response), (200 if health_response["status"] == "healthy" else 503) 

if __name__ == "__main__":
  app.run(debug=True)