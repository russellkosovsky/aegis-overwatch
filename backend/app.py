# backend/app.py

from flask import Flask, jsonify, render_template, request
from aegis_simulator.models import Network, Message
from aegis_simulator.reporter import Reporter

# Initialize the Flask application.
# The `__name__` argument helps Flask find static and template files.
app = Flask(__name__)

# --- Global Simulation State ---
# This section initializes the core Aegis network simulator when the server starts.
# It's kept in memory for the lifetime of the application.
print("--- Initializing Aegis Network ---")
network_reporter = Reporter()
network = Network.create_from_config("network_config.yml", reporter=network_reporter)
print("--- Network Ready ---")
# ---


# --- API Endpoints ---


@app.route("/api/network/graph-data")
def get_network_graph_data():
    """Provides network data formatted for a graph library like Vis.js.

    This endpoint is polled by the frontend to get the complete, current state
    of the network for visualization.

    Returns:
        Response: A JSON object containing two keys: 'nodes' and 'edges'.
                  Nodes include their ID, label, and color based on status.
                  Edges include their source, target, and latency label.
    """
    nodes, edges, seen_edges = [], [], set()
    for node in network.nodes.values():
        nodes.append(
            {
                "id": node.id,
                "label": node.name,
                "color": "#4ade80" if node.is_active else "#f87171",
            }
        )
        for neighbor, latency in node.neighbors.items():
            edge_tuple = tuple(sorted((node.id, neighbor.id)))
            if edge_tuple not in seen_edges:
                edges.append(
                    {"from": node.id, "to": neighbor.id, "label": f"{latency}ms"}
                )
                seen_edges.add(edge_tuple)
    return jsonify({"nodes": nodes, "edges": edges})


@app.route("/api/nodes")
def get_node_names():
    """Returns a simple, sorted list of all node names.

    Used by the frontend to populate the dropdown selectors in the control panel.

    Returns:
        Response: A JSON array of strings (e.g., ["Node-A", "Node-B"]).
    """
    if not network.nodes:
        return jsonify([])
    return jsonify(sorted([node.name for node in network.nodes.values()]))


@app.route("/api/network/path", methods=["POST"])
def find_path():
    """Calculates the fastest path between two nodes.

    Expects a JSON payload with 'from_node' and 'to_node' keys.

    Returns:
        Response: On success, a JSON object with the path and total latency.
                  On failure, a 404 error with a JSON error message.
    """
    data = request.get_json()
    from_node = network.get_node_by_name(data.get("from_node"))
    to_node = network.get_node_by_name(data.get("to_node"))
    if not from_node or not to_node:
        return jsonify({"error": "Nodes not found"}), 404
    path, latency = network.find_shortest_path(from_node.id, to_node.id)
    if path:
        return jsonify({"path": [n.name for n in path], "latency": latency})
    return jsonify({"error": "No path found"}), 404


@app.route("/api/network/route", methods=["POST"])
def route_message():
    """Routes a message between two nodes.

    Expects a JSON payload with 'from_node', 'to_node', and 'payload' keys.

    Returns:
        Response: A JSON object indicating success or failure.
    """
    data = request.get_json()
    from_node = network.get_node_by_name(data.get("from_node"))
    to_node = network.get_node_by_name(data.get("to_node"))
    payload = data.get("payload", "")
    if not from_node or not to_node:
        return jsonify({"error": "Nodes not found"}), 404
    message = Message(from_node.id, to_node.id, payload)
    if network.route_message(message):
        return jsonify({"success": True, "message": "Message routed successfully."})
    return (
        jsonify({"success": False, "message": "Routing failed. No path available."}),
        400,
    )


@app.route("/api/events")
def get_events():
    """Returns the 10 most recent simulation events from the reporter.

    Returns:
        Response: A JSON array of event log dictionaries.
    """
    recent_events = reversed(network_reporter.log_entries[-10:])
    return jsonify(list(recent_events))


@app.route("/api/node/<node_name>/offline", methods=["POST"])
def take_node_offline(node_name):
    """Takes a specific node offline.

    Args:
        node_name (str): The name of the node to take offline, from the URL.

    Returns:
        Response: A JSON object indicating success or failure.
    """
    node = network.get_node_by_name(node_name)
    if not node:
        return jsonify({"error": "Node not found"}), 404
    network_reporter.log_entries.append(
        {
            "timestamp": Reporter.get_timestamp(),
            "event_type": "STATUS_CHANGE",
            "details": f"Node '{node.name}' taken OFFLINE.",
        }
    )
    node.take_offline()
    return jsonify({"success": True, "status": "offline"})


@app.route("/api/node/<node_name>/online", methods=["POST"])
def bring_node_online(node_name):
    """Brings a specific node online.

    Args:
        node_name (str): The name of the node to bring online, from the URL.

    Returns:
        Response: A JSON object indicating success or failure.
    """
    node = network.get_node_by_name(node_name)
    if not node:
        return jsonify({"error": "Node not found"}), 404
    network_reporter.log_entries.append(
        {
            "timestamp": Reporter.get_timestamp(),
            "event_type": "STATUS_CHANGE",
            "details": f"Node '{node.name}' brought ONLINE.",
        }
    )
    node.bring_online()
    return jsonify({"success": True, "status": "online"})


# --- Frontend Serving ---


@app.route("/")
def index():
    """Serves the main HTML page for the dashboard."""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
