# tests/test_reporter.py

import os
import csv
from src.reporter import Reporter
from src.models import Message, Node

# Note: We need to create mock/dummy objects for the test.
# We can't use the full Network class as it's too complex for this unit test.


def test_reporter_writes_correct_csv(tmp_path):
    """
    Tests that the Reporter class correctly logs events and writes them
    to a CSV file in a temporary directory.

    Args:
        tmp_path: A pytest fixture that provides a temporary directory path.
    """
    # 1. SETUP
    reporter = Reporter()

    # Create dummy nodes and a message for logging
    node_a = Node("NodeA")
    node_b = Node("NodeB")
    node_c = Node("NodeC")
    message1 = Message(node_a.id, node_c.id, "Successful test message")
    message2 = Message(node_a.id, node_b.id, "Failed test message")

    # Log a successful event
    path = [node_a, node_c]
    reporter.log_routing_attempt(
        message=message1,
        source_node=node_a,
        dest_node=node_c,
        path=path,
        latency=50,
        success=True,
    )

    # Log a failed event
    reporter.log_routing_attempt(
        message=message2,
        source_node=node_a,
        dest_node=node_b,
        path=None,  # No path was found
        latency=0,
        success=False,
    )

    # 2. ACTION
    # Define the output file path within the temporary directory
    report_file = tmp_path / "test_report.csv"

    # Use os.path.join to be explicit, though '/' works with pathlib objects
    reporter.write_report(str(report_file))

    # 3. ASSERTION
    # Check that the file was actually created
    assert os.path.exists(report_file)

    # Read the created file and verify its contents
    with open(report_file, "r", newline="") as f:
        reader = csv.reader(f)
        # Read all rows into a list
        rows = list(reader)

        # Check the header row
        expected_header = [
            "timestamp",
            "message_id",
            "source_node",
            "intended_destination",
            "payload",
            "status",
            "path_taken",
            "total_latency_ms",
        ]
        assert rows[0] == expected_header

        # Check the data rows
        # Row 1 (Success)
        assert rows[1][2] == "NodeA"  # source_node
        assert rows[1][3] == "NodeC"  # intended_destination
        assert rows[1][5] == "SUCCESS"  # status
        assert rows[1][6] == "NodeA -> NodeC"  # path_taken
        assert rows[1][7] == "50"  # total_latency_ms

        # Row 2 (Failure)
        assert rows[2][2] == "NodeA"  # source_node
        assert rows[2][3] == "NodeB"  # intended_destination
        assert rows[2][5] == "FAILED"  # status
        assert rows[2][6] == "No path found"  # path_taken
        assert rows[2][7] == "N/A"  # total_latency_ms
