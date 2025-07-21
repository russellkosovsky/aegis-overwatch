# backend/tests/test_reporter.py

import os
import csv
from unittest.mock import patch
from aegis_simulator.reporter import Reporter
from aegis_simulator.models import Message, Node

def test_reporter_writes_correct_csv(tmp_path):
    """
    Tests that the Reporter class correctly logs events and writes them
    to a CSV file in a temporary directory.
    """
    reporter = Reporter()
    
    node_a = Node("NodeA")
    node_b = Node("NodeB")
    node_c = Node("NodeC")
    message1 = Message(node_a.id, node_c.id, "Successful test message")
    message2 = Message(node_a.id, node_b.id, "Failed test message")

    path = [node_a, node_c]
    reporter.log_routing_attempt(
        message=message1, source_node=node_a, dest_node=node_c,
        path=path, latency=50, success=True
    )
    reporter.log_routing_attempt(
        message=message2, source_node=node_a, dest_node=node_b,
        path=None, latency=0, success=False
    )

    report_file = tmp_path / "test_report.csv"
    
    with patch('os.makedirs'):
        reporter.write_report(str(report_file))

    assert os.path.exists(report_file)

    with open(report_file, 'r', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        expected_header = [
            "timestamp", "event_type", "details", "status", 
            "path_taken", "total_latency_ms"
        ]
        assert rows[0] == expected_header
        
        # Row 1 (Success)
        assert rows[1][2] == "Route from 'NodeA' to 'NodeC' SUCCEEDED."
        assert rows[1][3] == "SUCCESS"
        assert rows[1][4] == "NodeA -> NodeC"
        assert rows[1][5] == "50"

        # Row 2 (Failure)
        assert rows[2][2] == "Route from 'NodeA' to 'NodeB' FAILED."
        assert rows[2][3] == "FAILED"
        assert rows[2][4] == "No path found"
        assert rows[2][5] == "N/A"