# src/visualizer.py

import matplotlib

matplotlib.use("Agg")  # Set non-GUI backend for CI/CD environments

import networkx as nx
import matplotlib.pyplot as plt
import os


class Visualizer:
    """Handles the creation of network graph visualizations."""

    def generate_graph_image(self, network, filename="network_topology.png"):
        """Creates a visual graph of the network and saves it as a PNG image.

        This method uses the networkx and matplotlib libraries to draw a
        representation of the network's current state. The resulting image
        is saved in the `output/png/` directory.

        - Nodes are colored based on their active status (Green for ONLINE, Red for OFFLINE).
        - Node labels are displayed above the nodes for clarity.
        - Edges (links) are labeled with their latency.

        Args:
            network (Network): The network object to visualize.
            filename (str, optional): The name for the output PNG file.
                                      Defaults to "network_topology.png".
        """
        output_dir = os.path.join("output", "png")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        if not network.nodes:
            print("Cannot generate graph: Network has no nodes.")
            return

        G = nx.Graph()

        node_colors = []
        node_labels = {}

        for node in network.nodes.values():
            G.add_node(node.id)
            node_labels[node.id] = node.name
            node_colors.append("green" if node.is_active else "red")

        edge_labels = {}
        for node in network.nodes.values():
            for neighbor, latency in node.neighbors.items():
                if not G.has_edge(node.id, neighbor.id):
                    G.add_edge(node.id, neighbor.id)
                    edge_labels[(node.id, neighbor.id)] = f"{latency}ms"

        pos = nx.spring_layout(G, k=2.0, iterations=50)

        plt.figure(figsize=(16, 12))

        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1500)
        nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7, edge_color="gray")
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels, font_color="black", font_size=9
        )

        label_pos = {k: (v[0], v[1] + 0.08) for k, v in pos.items()}
        nx.draw_networkx_labels(
            G, label_pos, labels=node_labels, font_size=12, font_color="black"
        )

        plt.title("Project Aegis - Network Topology", size=20)
        plt.margins(0.1)
        plt.axis("off")

        try:
            plt.savefig(filepath, format="PNG", bbox_inches="tight")
            print(f"Successfully saved network graph to '{filepath}'")
        except IOError as e:
            print(f"Error saving graph image: {e}")
        finally:
            plt.clf()
            plt.close()
