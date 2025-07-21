# src/reporter.py

import csv
import datetime
import os


class Reporter:
    """Logs simulation events and generates a CSV report.

    This class collects data from each message routing attempt and can
    write the aggregated data to a CSV file for analysis.

    Attributes:
        log_entries (list): A list of dictionaries, where each dictionary
                            represents a single logged event.
    """

    def __init__(self):
        """Initializes the reporter with an empty log."""
        self.log_entries = []
        print("Reporter initialized.")

    def log_routing_attempt(
        self, message, source_node, dest_node, path, latency, success
    ):
        """Logs the result of a single message routing attempt.

        This method is called by the Network class after each routing attempt.

        Args:
            message (Message): The message object that was routed.
            source_node (Node): The originating node.
            dest_node (Node): The intended destination node.
            path (list or None): A list of Node objects representing the path taken,
                                 or None if no path was found.
            latency (int or float): The total latency of the path.
            success (bool): True if the message was successfully delivered,
                            False otherwise.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = {
            "timestamp": timestamp,
            "message_id": message.id,
            "source_node": source_node.name,
            "intended_destination": dest_node.name,
            "payload": message.payload,
            "status": "SUCCESS" if success else "FAILED",
            "path_taken": (
                " -> ".join([n.name for n in path]) if path else "No path found"
            ),
            "total_latency_ms": latency if success else "N/A",
        }
        self.log_entries.append(entry)

    def write_report(self, filename="simulation_report.csv"):
        """Writes all logged entries to a specified CSV file.

        The report is saved in the `output/csv/` directory.

        Args:
            filename (str, optional): The name for the output CSV file.
                                      Defaults to "simulation_report.csv".

        Returns:
            bool: True if the report was written successfully, False otherwise.
        """
        output_dir = os.path.join("output", "csv")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        if not self.log_entries:
            print("No events to report.")
            return False

        headers = self.log_entries[0].keys()

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(self.log_entries)
            print(f"Successfully wrote report to '{filepath}'")
            return True
        except IOError as e:
            print(f"Error writing report to file: {e}")
            return False
