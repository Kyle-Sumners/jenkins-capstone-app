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
  color = "#2e7d32" if database_up() else "#c62828"

  return f"""
     <style>
      body {{
        font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
        background: #f4f5f6;
        display: flex;
        justify-content: center;
        padding-top: 8vh;
      }}
      .card {{
        background: #fff;
        border-radius: 10px;
        padding: 3rem 4rem;
        box-shadow: 0 2px 12px rgba(0,0,0,.08);
        text-align: center;
      }}
      h1 {{ margin: 0 0 1.5rem; color: #0f3a5f; }}
      .version {{ font-size: 3rem; font-weight: 700; color: #0f3a5f; }}
      .label {{ color: #6b7c86; letter-spacing: .08em; font-size: .8rem; }}
      .status {{
        margin-top: 1.5rem; padding: .5rem 1.5rem; border-radius: 999px;
        display: inline-block; color: #fff; background: {color};
      }}
    </style>
    <div class="card">
      <h1>Capstone Application</h1>
      <div class="label">VERSION:</div> 
      <div class="version">{current_version()}</div>
      <div class="status">Status: {status}</div>
    </div>
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