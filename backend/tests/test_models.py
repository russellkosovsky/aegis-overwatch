# tests/test_models.py

import yaml
import pytest
from src.models import Node, Message, Network

# --- Node & Basic Network Tests ---


def test_node_creation():
    """Tests that a Node object is created with a name and a unique ID."""
    node1 = Node(name="Ground Station Alpha")
    assert node1.name == "Ground Station Alpha"
    assert node1.id is not None
    assert len(node1.neighbors) == 0
    assert node1.is_active is True


def test_add_neighbor_is_bilateral():
    """Tests that connecting two nodes works in both directions with latency."""
    node1 = Node(name="Command Center")
    node2 = Node(name="Mobile Unit 7")
    latency = 20
    node1.add_neighbor(node2, latency)

    assert node2 in node1.neighbors
    assert node1.neighbors[node2] == latency
    assert node1 in node2.neighbors
    assert node2.neighbors[node1] == latency


def test_network_add_node():
    """Tests that a node can be successfully added to the network."""
    network = Network()
    node = Node("Test Node")
    network.add_node(node)

    assert len(network.nodes) == 1
    assert network.get_node(node.id) == node


# --- Message Sending Tests ---


def test_send_direct_message_success():
    """Tests successfully sending a message between two direct neighbors."""
    network = Network()
    node_a = Node("A")
    node_b = Node("B")
    network.add_node(node_a)
    network.add_node(node_b)
    node_a.add_neighbor(node_b, 10)

    message = Message(source_id=node_a.id, destination_id=node_b.id, payload="Hello")
    assert network.send_direct_message(message) is True


def test_send_direct_message_failure_not_neighbors():
    """Tests that a message cannot be sent between two nodes that are not neighbors."""
    network = Network()
    node_a = Node("A")
    node_b = Node("B")
    network.add_node(node_a)
    network.add_node(node_b)

    message = Message(
        source_id=node_a.id, destination_id=node_b.id, payload="This should fail"
    )
    assert network.send_direct_message(message) is False


def test_node_receives_correct_message():
    """Tests that a node correctly processes a message intended for it."""
    node_a = Node("Receiver Node")
    message = Message(
        source_id="some_other_node", destination_id=node_a.id, payload="Test"
    )
    assert node_a.receive_message(message) is True


def test_node_rejects_incorrect_message():
    """Tests that a node rejects a message not intended for it."""
    node_a = Node("Receiver Node")
    message = Message(
        source_id="some_other_node", destination_id="a_different_id", payload="Wrong"
    )
    assert node_a.receive_message(message) is False


# --- Config and Pathfinding Tests ---


def test_create_network_from_config(tmp_path):
    """
    Tests that a network can be created from a YAML configuration dictionary.
    """
    config_content = """
    nodes:
      - name: Node A
      - name: Node B
      - name: Node C
    links:
      - [Node A, Node B, 25]
    """
    # --- MODIFIED: Load the YAML data into a dictionary first ---
    config_data = yaml.safe_load(config_content)

    # Create the network from the loaded dictionary
    network = Network.create_from_config(config_data)

    assert len(network.nodes) == 3
    node_a = network.get_node_by_name("Node A")
    node_b = network.get_node_by_name("Node B")
    node_c = network.get_node_by_name("Node C")

    assert node_a is not None
    assert node_b is not None
    assert node_c is not None

    assert node_b in node_a.neighbors
    assert node_a.neighbors[node_b] == 25
    assert len(node_c.neighbors) == 0


def test_find_shortest_path_no_path():
    """Tests that the algorithm returns None when no path exists."""
    network = Network()
    node_a = Node("A")
    node_b = Node("B")
    network.add_node(node_a)
    network.add_node(node_b)

    path, latency = network.find_shortest_path(node_a.id, node_b.id)
    assert path is None
    assert latency == float("inf")


# --- Resilience Tests (Offline/Online Nodes) ---


def test_node_can_be_taken_offline_and_online():
    """Tests that a node's active status can be toggled."""
    node = Node("Test Node")
    assert node.is_active is True
    node.take_offline()
    assert node.is_active is False
    node.bring_online()
    assert node.is_active is True


def test_pathfinder_avoids_offline_nodes():
    """Tests that the pathfinder finds an alternate route around an offline node."""
    network = Network()
    node_a = Node("A")
    node_b = Node("B")
    node_c = Node("C")
    network.add_node(node_a)
    network.add_node(node_b)
    network.add_node(node_c)

    node_a.add_neighbor(node_b, 100)
    node_b.add_neighbor(node_c, 100)
    node_a.add_neighbor(node_c, 500)

    node_b.take_offline()

    path, latency = network.find_shortest_path(node_a.id, node_c.id)
    assert path is not None
    assert latency == 500
    assert len(path) == 2
    assert path[0].name == "A"
    assert path[1].name == "C"


def test_pathfinder_fails_if_no_alternate_path():
    """Tests that the pathfinder returns None if an offline node breaks the only path."""
    network = Network()
    node_a = Node("A")
    node_b = Node("B")
    node_c = Node("C")
    network.add_node(node_a)
    network.add_node(node_b)
    network.add_node(node_c)
    node_a.add_neighbor(node_b, 10)
    node_b.add_neighbor(node_c, 10)

    node_b.take_offline()
    path, latency = network.find_shortest_path(node_a.id, node_c.id)
    assert path is None


# --- Dijkstra-Specific Test ---


def test_dijkstra_finds_fastest_path_not_shortest_hops():
    """
    Tests that Dijkstra's algorithm correctly chooses a path with lower total
    latency, even if it has more hops.
    """
    network = Network()
    node_a = Node("A")
    node_b = Node("B")
    node_c = Node("C")
    network.add_node(node_a)
    network.add_node(node_b)
    network.add_node(node_c)

    node_a.add_neighbor(node_b, 30)
    node_a.add_neighbor(node_c, 10)
    node_c.add_neighbor(node_b, 10)

    path, latency = network.find_shortest_path(node_a.id, node_b.id)
    assert path is not None
    assert latency == 20
    assert len(path) == 3
    assert path[0].name == "A"
    assert path[1].name == "C"
    assert path[2].name == "B"


# --- Full Routing Logic Tests ---


def test_route_message_success():
    """Tests that a message is successfully routed along the fastest path."""
    network = Network()
    node_a = Node("A")
    node_b = Node("B")
    node_c = Node("C")
    network.add_node(node_a)
    network.add_node(node_b)
    network.add_node(node_c)
    node_a.add_neighbor(node_b, 10)
    node_b.add_neighbor(node_c, 10)

    message = Message(node_a.id, node_c.id, "Test message")
    assert network.route_message(message) is True


def test_route_message_failure_no_path():
    """Tests that routing fails if no path can be found."""
    network = Network()
    node_a = Node("A")
    node_b = Node("B")
    network.add_node(node_a)
    network.add_node(node_b)

    message = Message(node_a.id, node_b.id, "Message to nowhere")
    assert network.route_message(message) is False
