import os
import unittest
from pysqa import QueueAdapter

try:
    import paramiko
    from tqdm import tqdm

    skip_multi_test = False
except ImportError:
    skip_multi_test = True


@unittest.skipIf(
    skip_multi_test,
    "Either paramiko or tqdm are not installed, so the multi queue adapter tests are skipped.",
)
class TestMultiQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.multi = QueueAdapter(
            directory=os.path.join(cls.path, "config/multicluster")
        )

    def test_config(self):
        self.assertEqual(self.multi.config["queue_type"], "SLURM")
        self.assertEqual(self.multi.config["queue_primary"], "slurm")

    def test_list_clusters(self):
        self.assertEqual(self.multi.list_clusters(), ["local_slurm", "remote_slurm"])
