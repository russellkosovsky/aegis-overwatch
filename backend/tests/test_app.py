# backend/tests/test_app.py

import pytest
import json
from unittest.mock import patch

# Import the Flask app object from your app file
from app import app as flask_app
from aegis_simulator.models import Network, Node


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # This fixture ensures that each test gets a clean, fresh app
    # so that tests don't interfere with each other.
    yield flask_app


@pytest.fixture
def client(app):
    """A test client for the app."""
    # The test client allows us to make requests to our API endpoints
    # without running a live server.
    return app.test_client()


# We use a patch here to prevent the real app from loading the real config file.
# This makes our tests faster and more predictable.
@patch("app.Network.create_from_config")
def test_get_graph_data_endpoint(mock_create_config, client):
    """
    Tests the GET /api/network/graph-data endpoint.
    """
    # 1. SETUP
    # Create a simple, predictable network for our test
    test_network = Network()
    node_a = Node("Node-A")
    node_b = Node("Node-B")
    node_a.add_neighbor(node_b, 50)
    test_network.add_node(node_a)
    test_network.add_node(node_b)

    # Tell our mock to use this test network instead of loading from a file
    mock_create_config.return_value = test_network

    # We need to patch the global 'network' object inside the 'app' module
    with patch("app.network", test_network):
        # 2. ACTION
        # Use the test client to make a GET request to our endpoint
        response = client.get("/api/network/graph-data")

        # 3. ASSERTION
        # Check that the server responded with a 200 OK status
        assert response.status_code == 200

        # Parse the JSON data from the response
        data = json.loads(response.data)

        # Check that the data has the correct structure
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 1
        assert data["nodes"][0]["label"] == "Node-A"
        assert data["edges"][0]["label"] == "50ms"


@patch("app.Network.create_from_config")
def test_take_node_offline_endpoint(mock_create_config, client):
    """
    Tests the POST /api/node/<node_name>/offline endpoint.
    This test verifies both the direct response and the side effect.
    """
    # 1. SETUP
    test_network = Network()
    node_a = Node("Node-A")
    test_network.add_node(node_a)
    mock_create_config.return_value = test_network

    with patch("app.network", test_network):
        # 2. ACTION (Part 1)
        # Make a POST request to take the node offline
        response = client.post("/api/node/Node-A/offline")

        # 3. ASSERTION (Part 1)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["status"] == "offline"

        # 4. VERIFY THE SIDE EFFECT
        # Check that the node is actually offline now by calling the graph endpoint
        response_after = client.get("/api/network/graph-data")
        data_after = json.loads(response_after.data)

        node_a_data = data_after["nodes"][0]
        assert node_a_data["label"] == "Node-A"
        # The color should now be the "offline" color
        assert node_a_data["color"] == "#f87171"
