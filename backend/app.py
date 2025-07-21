# backend/app.py

from flask import Flask, jsonify, render_template, request
from aegis_simulator.models import Network, Message
from aegis_simulator.reporter import Reporter

app = Flask(__name__)

# --- Global Simulation State ---
print("--- Initializing Aegis Network ---")
network_reporter = Reporter()
network = Network.create_from_config("network_config.yml", reporter=network_reporter)
print("--- Network Ready ---")
# ---

# --- API Endpoints ---


@app.route("/api/network/graph-data")
def get_network_graph_data():
    """Provides network data formatted for a graph library like Vis.js."""
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
    """Returns a sorted list of all node names."""
    if not network.nodes:
        return jsonify([])
    return jsonify(sorted([node.name for node in network.nodes.values()]))


@app.route("/api/network/path", methods=["POST"])
def find_path():
    """Calculates the fastest path between two nodes."""
    data = request.get_json()
    from_node, to_node = network.get_node_by_name(
        data.get("from_node")
    ), network.get_node_by_name(data.get("to_node"))
    if not from_node or not to_node:
        return jsonify({"error": "Nodes not found"}), 404
    path, latency = network.find_shortest_path(from_node.id, to_node.id)
    if path:
        return jsonify({"path": [n.name for n in path], "latency": latency})
    return jsonify({"error": "No path found"}), 404


@app.route("/api/network/route", methods=["POST"])
def route_message():
    """Routes a message between two nodes."""
    data = request.get_json()
    from_node, to_node = network.get_node_by_name(
        data.get("from_node")
    ), network.get_node_by_name(data.get("to_node"))
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


# --- NEW: Endpoint for PO-6 ---
@app.route("/api/events")
def get_events():
    """Returns the 10 most recent simulation events."""
    # Return events in reverse chronological order (newest first)
    recent_events = reversed(network_reporter.log_entries[-10:])
    return jsonify(list(recent_events))


@app.route("/api/node/<node_name>/offline", methods=["POST"])
def take_node_offline(node_name):
    node = network.get_node_by_name(node_name)
    if not node:
        return jsonify({"error": "Node not found"}), 404
    # --- NEW: Manually log this event since it doesn't involve routing ---
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
    node = network.get_node_by_name(node_name)
    if not node:
        return jsonify({"error": "Node not found"}), 404
    # --- NEW: Manually log this event ---
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
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
