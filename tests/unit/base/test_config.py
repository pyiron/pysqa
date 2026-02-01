import unittest
from pysqa.base.config import QueueAdapterWithConfig


class TestConfig(unittest.TestCase):
    def test_bad_queue_type(self):
        with self.assertRaises(ValueError):
            QueueAdapterWithConfig(config={"queue_type": "error", "queues": {}})
