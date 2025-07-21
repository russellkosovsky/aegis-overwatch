# backend/aegis_simulator/reporter.py

import csv
import datetime
import os


class Reporter:
    """Logs simulation events and generates a CSV report."""

    def __init__(self):
        """Initializes the reporter with an empty log."""
        self.log_entries = []
        print("Reporter initialized.")

    @staticmethod
    def get_timestamp():
        """Returns a consistently formatted timestamp string."""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log_routing_attempt(
        self, message, source_node, dest_node, path, latency, success
    ):
        """Logs the result of a single message routing attempt."""
        entry = {
            "timestamp": self.get_timestamp(),
            "event_type": "MESSAGE_ROUTE",
            "details": f"Route from '{source_node.name}' to '{dest_node.name}' {'SUCCEEDED' if success else 'FAILED'}.",
            "status": "SUCCESS" if success else "FAILED",
            "path_taken": (
                " -> ".join([n.name for n in path]) if path else "No path found"
            ),
            "total_latency_ms": latency if success else "N/A",
        }
        self.log_entries.append(entry)

    def write_report(self, filename="simulation_report.csv"):
        """Writes all logged entries to a specified CSV file."""
        output_dir = os.path.join("output", "csv")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        if not self.log_entries:
            print("No events to report.")
            return False

        # Dynamically get headers from the first entry to handle different event types
        headers = self.log_entries[0].keys()

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(self.log_entries)
            print(f"Successfully wrote report to '{filepath}'")
            return True
        except IOError as e:
            print(f"Error writing report to file: {e}")
            return False
