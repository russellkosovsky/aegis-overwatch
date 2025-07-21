# tests/test_main.py

import pytest
from unittest.mock import patch, mock_open
from io import StringIO

from main import main
from src.models import Network, Node


# We add more patches to prevent the test from accessing the real file system
@patch("main.validate_config", return_value=True)  # Assume validation always passes
@patch(
    "main.yaml.safe_load", return_value={"nodes": [], "links": []}
)  # Return dummy config data
@patch("builtins.open", new_callable=mock_open)  # Mock the file open call
@patch("main.Network.create_from_config")  # This is our original key mock
@patch("builtins.input", side_effect=["status", "exit", "n"])
@patch("sys.stdout", new_callable=StringIO)
def test_cli_status_command(
    mock_stdout, mock_input, mock_create_net, mock_open, mock_yaml, mock_validate
):
    """
    Tests the 'status' command of the CLI, now fully isolated from the file system.
    """
    # SETUP: Create the test network we want the mocked create_from_config to return
    test_network = Network()
    node_a = Node("Node-A")
    node_b = Node("Node-B")
    node_b.take_offline()
    test_network.add_node(node_a)
    test_network.add_node(node_b)
    mock_create_net.return_value = test_network

    # ACTION
    try:
        main()
    except StopIteration:
        pass

    # ASSERTION
    output = mock_stdout.getvalue()
    assert "Node-A" in output
    assert "ONLINE" in output
    assert "Node-B" in output
    assert "OFFLINE" in output


@patch("main.validate_config", return_value=True)
@patch("main.yaml.safe_load", return_value={"nodes": [], "links": []})
@patch("builtins.open", new_callable=mock_open)
@patch("main.Network.create_from_config")
@patch("builtins.input", side_effect=["path Node-A Node-C", "exit", "n"])
@patch("sys.stdout", new_callable=StringIO)
def test_cli_path_command(
    mock_stdout, mock_input, mock_create_net, mock_open, mock_yaml, mock_validate
):
    """Tests the 'path' command of the CLI, now fully isolated."""
    # SETUP
    network = Network()
    node_a = Node("Node-A")
    node_b = Node("Node-B")
    node_c = Node("Node-C")
    network.add_node(node_a)
    network.add_node(node_b)
    network.add_node(node_c)
    node_a.add_neighbor(node_b, 10)
    node_b.add_neighbor(node_c, 10)
    mock_create_net.return_value = network

    # ACTION
    try:
        main()
    except StopIteration:
        pass

    # ASSERTION
    output = mock_stdout.getvalue()
    assert "Fastest Path: Node-A -> Node-B -> Node-C" in output
    assert "(Latency: 20ms)" in output
