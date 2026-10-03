import unittest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scheduler import Process, fcfs, metrics, round_robin, sjf


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        self.processes = [Process("P1", 0, 5), Process("P2", 1, 2), Process("P3", 2, 1)]

    def test_fcfs_orders_by_arrival(self):
        self.assertEqual([(item.pid, item.start, item.end) for item in fcfs(self.processes)], [("P1", 0, 5), ("P2", 5, 7), ("P3", 7, 8)])

    def test_sjf_chooses_shortest_ready_job(self):
        self.assertEqual([item.pid for item in sjf(self.processes)], ["P1", "P3", "P2"])

    def test_round_robin_rotates_processes(self):
        timeline = round_robin(self.processes, 2)
        self.assertEqual([item.pid for item in timeline], ["P1", "P2", "P3", "P1"])
        self.assertEqual(timeline[-1].end, 8)

    def test_metrics_include_waiting_and_response_time(self):
        result = {row["pid"]: row for row in metrics(self.processes, fcfs(self.processes))}
        self.assertEqual(result["P2"]["waiting"], 4)
        self.assertEqual(result["P3"]["response"], 5)

    def test_invalid_quantum_is_rejected(self):
        with self.assertRaises(ValueError):
            round_robin(self.processes, 0)


if __name__ == "__main__":
    unittest.main()

