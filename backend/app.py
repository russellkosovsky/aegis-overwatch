# backend/app.py

from flask import Flask, jsonify, render_template, request
from aegis_simulator.models import Network
from aegis_simulator.reporter import Reporter

app = Flask(__name__)

# --- Global Simulation State ---
print("--- Initializing Aegis Network ---")
network_reporter = Reporter() 
network = Network.create_from_config("network_config.yml", reporter=network_reporter)
print("--- Network Ready ---")
# ---

# --- API Endpoints ---

@app.route("/api/network/status")
def get_network_status():
    """API endpoint to get the current status of all nodes and links."""
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
    return jsonify(sorted(nodes_data, key=lambda x: x['name']))

# --- NEW: API Control Endpoints for PO-2 ---

@app.route("/api/node/<node_name>/offline", methods=['POST'])
def take_node_offline(node_name):
    """API endpoint to take a specific node offline."""
    node = network.get_node_by_name(node_name)
    if not node:
        return jsonify({"error": "Node not found"}), 404
    
    node.take_offline()
    print(f"API: Took node '{node_name}' offline.")
    return jsonify({"success": True, "node_name": node_name, "status": "offline"})

@app.route("/api/node/<node_name>/online", methods=['POST'])
def bring_node_online(node_name):
    """API endpoint to bring a specific node online."""
    node = network.get_node_by_name(node_name)
    if not node:
        return jsonify({"error": "Node not found"}), 404
    
    node.bring_online()
    print(f"API: Brought node '{node_name}' online.")
    return jsonify({"success": True, "node_name": node_name, "status": "online"})

# --- Frontend Serving ---

@app.route("/")
def index():
    """Serves the main HTML page for the dashboard."""
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
