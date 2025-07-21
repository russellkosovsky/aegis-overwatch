# backend/app.py

from flask import Flask, jsonify, render_template
from aegis_simulator.models import Network
from aegis_simulator.reporter import Reporter

# Initialize the Flask application
app = Flask(__name__)

# --- Global Simulation State ---
# In a real application, this might be in a database, but for our
# simulator, we can load it once and keep it in memory.
print("--- Initializing Aegis Network ---")
# We don't need a real reporter for the web UI yet
network_reporter = Reporter() 
# NOTE: This assumes you have a valid network_config.yml in the same
# directory as where you run the flask app (the 'backend' folder).
# You may need to copy it from your Aegis project.
network = Network.create_from_config("network_config.yml", reporter=network_reporter)
print("--- Network Ready ---")
# ---

# --- API Endpoints ---

@app.route("/api/network/status")
def get_network_status():
    """
    API endpoint to get the current status of all nodes and links.
    Returns data in JSON format.
    """
    nodes_data = []
    for node in network.nodes.values():
        nodes_data.append({
            "id": node.id,
            "name": node.name,
            "is_active": node.is_active,
            "neighbors": [
                {"name": neighbor.name, "latency": latency} 
                for neighbor, latency in node.neighbors.items()
            ]
        })
    
    # Use jsonify to properly format the response as JSON
    return jsonify(sorted(nodes_data, key=lambda x: x['name']))

# --- Frontend Serving ---

@app.route("/")
def index():
    """
    Serves the main HTML page for the dashboard.
    """
    # Flask will automatically look for this file in the 'templates' folder.
    return render_template("index.html")

if __name__ == "__main__":
    # Runs the Flask development server.
    # debug=True allows the server to auto-reload when you save changes.
    app.run(debug=True)
