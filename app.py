from flask import Flask, jsonify
import os

app = Flask(__name__)

def current_version():
    return os.getenv("VERSION", "0.0.0")

def database_up():
    return os.getenv("DB_STATUS", "up") == "up"

@app.route("/")
def home():
  status = "healthy" if database_up() else "unhealthy"

  return f"""
    <h1>Hello, World!</h1>
    <p>Version: <strong>{current_version()}</strong></p>
    <p>Status: {status}</p>
  """

@app.route("/health", methods=['GET'])
def get_health():
  database_status = database_up()
  version = current_version()
  
  health_response = {
    "status": "healthy",
    "version": version,
    "checks": {
      "database": "up"
    }
  }

  if not database_status:
    health_response["status"] = "unhealthy"
    health_response["checks"]["database"] = "down"
  
  return jsonify(health_response), (200 if health_response["status"] == "healthy" else 503) 

if __name__ == "__main__":
  app.run(debug=True)