# backend/tests/test_models.py

import yaml
import pytest
from aegis_simulator.models import Node, Message, Network

def test_node_creation():
    node1 = Node(name="Ground Station Alpha")
    assert node1.name == "Ground Station Alpha"
    assert node1.id is not None
    assert len(node1.neighbors) == 0
    assert node1.is_active is True

def test_add_neighbor_is_bilateral():
    node1 = Node(name="Command Center")
    node2 = Node(name="Mobile Unit 7")
    node1.add_neighbor(node2, 20)
    assert node2 in node1.neighbors
    assert node1.neighbors[node2] == 20
    assert node1 in node2.neighbors
    assert node2.neighbors[node1] == 20

def test_network_add_node():
    network = Network()
    node = Node("Test Node")
    network.add_node(node)
    assert len(network.nodes) == 1
    assert network.get_node(node.id) == node

def test_send_direct_message_success():
    network = Network()
    node_a, node_b = Node("A"), Node("B")
    network.add_node(node_a)
    network.add_node(node_b)
    node_a.add_neighbor(node_b, 10)
    message = Message(source_id=node_a.id, destination_id=node_b.id, payload="Hello")
    assert network.send_direct_message(message) is True

def test_send_direct_message_failure_not_neighbors():
    network = Network()
    node_a, node_b = Node("A"), Node("B")
    network.add_node(node_a)
    network.add_node(node_b)
    message = Message(source_id=node_a.id, destination_id=node_b.id, payload="This should fail")
    assert network.send_direct_message(message) is False

def test_node_receives_correct_message():
    node_a = Node("Receiver Node")
    message = Message(source_id="other", destination_id=node_a.id, payload="Test")
    assert node_a.receive_message(message) is True

def test_node_rejects_incorrect_message():
    node_a = Node("Receiver Node")
    message = Message(source_id="other", destination_id="different", payload="Wrong")
    assert node_a.receive_message(message) is False

def test_create_network_from_config(tmp_path):
    """
    Tests that a network can be created from a YAML configuration file.
    """
    config_content = """
    nodes:
      - name: Node A
      - name: Node B
    links:
      - [Node A, Node B, 25]
    """
    config_file = tmp_path / "test_config.yml"
    config_file.write_text(config_content)

    network = Network.create_from_config(str(config_file))

    assert len(network.nodes) == 2
    node_a = network.get_node_by_name("Node A")
    node_b = network.get_node_by_name("Node B")
    assert node_a is not None and node_b is not None
    assert node_b in node_a.neighbors
    assert node_a.neighbors[node_b] == 25

def test_find_shortest_path_no_path():
    network = Network()
    node_a, node_b = Node("A"), Node("B")
    network.add_node(node_a)
    network.add_node(node_b)
    path, latency = network.find_shortest_path(node_a.id, node_b.id)
    assert path is None
    assert latency == float('inf')

def test_node_can_be_taken_offline_and_online():
    node = Node("Test Node")
    assert node.is_active is True
    node.take_offline()
    assert node.is_active is False
    node.bring_online()
    assert node.is_active is True

def test_pathfinder_avoids_offline_nodes():
    network = Network()
    node_a, node_b, node_c = Node("A"), Node("B"), Node("C")
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

def test_pathfinder_fails_if_no_alternate_path():
    network = Network()
    node_a, node_b, node_c = Node("A"), Node("B"), Node("C")
    network.add_node(node_a)
    network.add_node(node_b)
    network.add_node(node_c)
    node_a.add_neighbor(node_b, 10)
    node_b.add_neighbor(node_c, 10)
    node_b.take_offline()
    path, latency = network.find_shortest_path(node_a.id, node_c.id)
    assert path is None

def test_dijkstra_finds_fastest_path_not_shortest_hops():
    network = Network()
    node_a, node_b, node_c = Node("A"), Node("B"), Node("C")
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

def test_route_message_success():
    network = Network()
    node_a, node_b, node_c = Node("A"), Node("B"), Node("C")
    network.add_node(node_a)
    network.add_node(node_b)
    network.add_node(node_c)
    node_a.add_neighbor(node_b, 10)
    node_b.add_neighbor(node_c, 10)
    message = Message(node_a.id, node_c.id, "Test message")
    assert network.route_message(message) is True

def test_route_message_failure_no_path():
    network = Network()
    node_a, node_b = Node("A"), Node("B")
    network.add_node(node_a)
    network.add_node(node_b)
    message = Message(node_a.id, node_b.id, "Message to nowhere")
    assert network.route_message(message) is False