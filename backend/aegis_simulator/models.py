# src/models.py

import uuid
import logging
import yaml
import heapq

# --- MODIFIED: Changed to a relative import ---
from .reporter import Reporter


class Message:
    """Represents a data packet or message moving through the network.

    Attributes:
        id (str): A unique identifier for the message.
        source_id (str): The ID of the node that originated the message.
        destination_id (str): The ID of the intended recipient node.
        payload (str): The content of the message.
    """

    def __init__(self, source_id, destination_id, payload):
        """Initializes a new Message instance."""
        self.id = str(uuid.uuid4())
        self.source_id = source_id
        self.destination_id = destination_id
        self.payload = payload
        logging.info(f"Message {self.id} created from {source_id} to {destination_id}")


class Node:
    """Represents a single communications node in the simulated network.

    Attributes:
        id (str): A unique identifier for the node.
        name (str): The human-readable name of the node.
        neighbors (dict): A dictionary mapping neighboring Node objects to the
                          latency (int) of the link.
        is_active (bool): The operational status of the node (True for online,
                          False for offline).
    """

    def __init__(self, name):
        """Initializes a new Node instance."""
        self.id = str(uuid.uuid4())
        self.name = name
        self.neighbors = {}
        self.is_active = True
        logging.info(f"Node '{self.name}' created with ID {self.id}")

    def take_offline(self):
        """Sets the node's status to inactive (offline)."""
        self.is_active = False
        logging.warning(f"Node '{self.name}' has been taken OFFLINE.")

    def bring_online(self):
        """Sets the node's status to active (online)."""
        self.is_active = True
        logging.info(f"Node '{self.name}' has been brought ONLINE.")

    def add_neighbor(self, neighbor_node, latency):
        """Establishes a bilateral connection to another node.

        Args:
            neighbor_node (Node): The node object to connect to.
            latency (int): The cost or latency of the link in milliseconds.
        """
        if neighbor_node not in self.neighbors:
            self.neighbors[neighbor_node] = latency
            neighbor_node.neighbors[self] = latency
            logging.info(
                f"Node '{self.name}' connected to '{neighbor_node.name}' with latency {latency}ms"
            )

    def receive_message(self, message):
        """Processes a message that has arrived at this node.

        Checks if this node is the final destination.

        Args:
            message (Message): The message object being received.

        Returns:
            bool: True if this node is the destination, False otherwise.
        """
        if self.id == message.destination_id:
            logging.info(
                f"Node '{self.name}' ({self.id}) received final message: '{message.payload}'"
            )
            return True
        return False


class Network:
    """Manages the entire collection of nodes and their interactions.

    This class is the main entry point for creating a network, finding paths,
    and routing messages.

    Attributes:
        nodes (dict): A dictionary mapping node IDs to their Node objects.
        reporter (Reporter): An instance of the Reporter class for logging events.
    """

    def __init__(self, reporter=None):
        """Initializes a new Network instance."""
        self.nodes = {}
        self.reporter = reporter if reporter else self._create_dummy_reporter()

    def _create_dummy_reporter(self):
        """Creates a non-functional reporter for when none is provided."""

        class DummyReporter:
            def log_routing_attempt(self, *args, **kwargs):
                pass

        return DummyReporter()

    def add_node(self, node):
        """Adds a node to the network's internal dictionary.

        Args:
            node (Node): The node object to add.
        """
        if node.id not in self.nodes:
            self.nodes[node.id] = node

    def get_node_by_name(self, name):
        """Retrieves a node from the network by its unique name.

        Args:
            name (str): The name of the node to find.

        Returns:
            Node or None: The found Node object, or None if not found.
        """
        for node in self.nodes.values():
            if node.name == name:
                return node
        return None

    def get_node(self, node_id):
        """Retrieves a node from the network by its ID.

        Args:
            node_id (str): The ID of the node to find.

        Returns:
            Node or None: The found Node object, or None if not found.
        """
        return self.nodes.get(node_id)

    def send_direct_message(self, message):
        """Sends a message to a direct neighbor. (Legacy/simple method).

        Args:
            message (Message): The message to send.

        Returns:
            bool: True if the message was sent successfully, False otherwise.
        """
        source_node = self.get_node(message.source_id)
        destination_node = self.get_node(message.destination_id)
        if not source_node or not destination_node:
            return False
        if destination_node in source_node.neighbors:
            return destination_node.receive_message(message)
        return False

    def set_link_latency(self, node1_name, node2_name, new_latency):
        """Updates the latency of an existing link between two nodes.

        Args:
            node1_name (str): The name of the first node.
            node2_name (str): The name of the second node.
            new_latency (int): The new latency value to set for the link.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        node1 = self.get_node_by_name(node1_name)
        node2 = self.get_node_by_name(node2_name)
        if not node1 or not node2:
            logging.error(
                f"Set latency failed: Node '{node1_name or node2_name}' not found."
            )
            return False
        if node2 in node1.neighbors:
            node1.neighbors[node2] = new_latency
            node2.neighbors[node1] = new_latency
            logging.info(
                f"Updated latency between '{node1.name}' and '{node2.name}' to {new_latency}ms."
            )
            return True
        logging.warning(
            f"Set latency failed: No direct link exists between '{node1.name}' and '{node2.name}'."
        )
        return False

    @classmethod
    def create_from_config(cls, config_path, reporter=None):
        """Factory method to create a Network instance from a YAML config file.

        Args:
            config_path (str): The file path to the YAML config file.
            reporter (Reporter, optional): An instance of the reporter. Defaults to None.

        Returns:
            Network: A new, configured Network object.
        """
        # --- MODIFIED: This method now handles opening the file itself ---
        network = cls(reporter=reporter)
        try:
            with open(config_path, "r") as f:
                config_data = yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            logging.error(f"Failed to load or parse config file: {e}")
            # Return an empty network on failure
            return network

        name_to_node_map = {}
        for node_data in config_data.get("nodes", []):
            node_name = node_data["name"]
            if node_name not in name_to_node_map:
                node = Node(name=node_name)
                network.add_node(node)
                name_to_node_map[node_name] = node
        for link_data in config_data.get("links", []):
            node1_name, node2_name, latency = link_data
            node1, node2 = name_to_node_map.get(node1_name), name_to_node_map.get(
                node2_name
            )
            if node1 and node2:
                node1.add_neighbor(node2, int(latency))
        return network

    def find_shortest_path(self, start_node_id, end_node_id):
        """Finds the fastest path between two nodes using Dijkstra's algorithm.

        The path is calculated based on the cumulative latency of the links,
        avoiding any nodes that are currently inactive.

        Args:
            start_node_id (str): The ID of the starting node.
            end_node_id (str): The ID of the destination node.

        Returns:
            tuple: A tuple containing the path (list of Node objects) and the
                   total latency (int). Returns (None, float('inf')) if no
                   path is found.
        """
        start_node, end_node = self.get_node(start_node_id), self.get_node(end_node_id)
        if not all([start_node, end_node, start_node.is_active, end_node.is_active]):
            return None, float("inf")

        distances = {node_id: float("inf") for node_id in self.nodes}
        distances[start_node_id] = 0
        previous_nodes = {node_id: None for node_id in self.nodes}
        pq = [(0, start_node_id)]

        while pq:
            current_latency, current_node_id = heapq.heappop(pq)
            if current_latency > distances[current_node_id]:
                continue
            current_node = self.get_node(current_node_id)
            if not current_node.is_active:
                continue
            if current_node_id == end_node_id:
                break
            for neighbor, latency in current_node.neighbors.items():
                if not neighbor.is_active:
                    continue
                distance = current_latency + latency
                if distance < distances[neighbor.id]:
                    distances[neighbor.id] = distance
                    previous_nodes[neighbor.id] = current_node
                    heapq.heappush(pq, (distance, neighbor.id))

        path = []
        current_node = end_node
        while current_node is not None:
            path.insert(0, current_node)
            current_node = previous_nodes.get(current_node.id)

        if path and path[0] == start_node:
            return path, distances[end_node_id]

        return None, float("inf")

    def route_message(self, message):
        """Routes a message from source to destination using the fastest path.

        This method uses `find_shortest_path` to determine the route and
        logs the attempt to the reporter.

        Args:
            message (Message): The message object to route.

        Returns:
            bool: True if the message was successfully delivered, False otherwise.
        """
        source_node, dest_node = self.get_node(message.source_id), self.get_node(
            message.destination_id
        )
        if not source_node or not dest_node:
            return False

        path, total_latency = self.find_shortest_path(source_node.id, dest_node.id)

        if not path:
            self.reporter.log_routing_attempt(
                message, source_node, dest_node, None, 0, False
            )
            return False

        success = path[-1].receive_message(message)
        self.reporter.log_routing_attempt(
            message, source_node, dest_node, path, total_latency, success
        )
        return success
