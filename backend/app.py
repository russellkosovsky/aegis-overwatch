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
    """(Legacy) API endpoint to get the current status of all nodes."""
    nodes_data = []
    for node in network.nodes.values():
        nodes_data.append({
            "id": node.id, "name": node.name, "is_active": node.is_active,
            "neighbors": [{"name": n.name, "latency": l} for n, l in node.neighbors.items()]
        })
    return jsonify(sorted(nodes_data, key=lambda x: x['name']))

# --- NEW: API Endpoint for Graph Visualization ---
@app.route("/api/network/graph-data")
def get_network_graph_data():
    """
    API endpoint that provides network data formatted for a graph library like Vis.js.
    """
    nodes = []
    edges = []
    seen_edges = set() # To prevent duplicate edges

    for node in network.nodes.values():
        # Add node data
        nodes.append({
            "id": node.id,
            "label": node.name,
            "color": "#4ade80" if node.is_active else "#f87171" # Green or Red
        })
        
        # Add edge data
        for neighbor, latency in node.neighbors.items():
            # Create a sorted tuple to uniquely identify each edge pair
            edge_tuple = tuple(sorted((node.id, neighbor.id)))
            if edge_tuple not in seen_edges:
                edges.append({
                    "from": node.id,
                    "to": neighbor.id,
                    "label": f"{latency}ms"
                })
                seen_edges.add(edge_tuple)

    return jsonify({"nodes": nodes, "edges": edges})


@app.route("/api/node/<node_name>/offline", methods=['POST'])
def take_node_offline(node_name):
    """API endpoint to take a specific node offline."""
    node = network.get_node_by_name(node_name)
    if not node: return jsonify({"error": "Node not found"}), 404
    node.take_offline()
    return jsonify({"success": True, "status": "offline"})

@app.route("/api/node/<node_name>/online", methods=['POST'])
def bring_node_online(node_name):
    """API endpoint to bring a specific node online."""
    node = network.get_node_by_name(node_name)
    if not node: return jsonify({"error": "Node not found"}), 404
    node.bring_online()
    return jsonify({"success": True, "status": "online"})

# --- Frontend Serving ---

@app.route("/")
def index():
    """Serves the main HTML page for the dashboard."""
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
