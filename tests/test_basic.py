import os
import unittest
from jinja2.exceptions import TemplateSyntaxError
from pysqa import QueueAdapter
from pysqa.base.config import QueueAdapterWithConfig
from pysqa.base.validate import value_in_range, check_queue_parameters


class TestQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))

    def test_missing_config(self):
        with self.assertRaises(ValueError):
            QueueAdapter(directory=os.path.join(self.path, "config/error"))

    def test_missing_config_folder(self):
        with self.assertRaises(ValueError):
            QueueAdapter(directory=os.path.join(self.path, "config"))

    def test_no_config(self):
        with self.assertRaises(ValueError):
            QueueAdapter()

    def test_bad_queue_template(self):
        with self.assertRaises(TemplateSyntaxError):
            QueueAdapter(directory=os.path.join(self.path, "config/bad_template"))


class TestBasisQueueAdapter(unittest.TestCase):
    def test_bad_queue_type(self):
        with self.assertRaises(ValueError):
            QueueAdapterWithConfig(config={"queue_type": "error", "queues": {}})

    def test_memory_string_comparison(self):
        self.assertEqual(value_in_range(1023, value_min="1K"), "1K")
        self.assertEqual(value_in_range(1035, value_min="1K"), 1035)
        self.assertEqual(value_in_range(1035, value_max="1K"), "1K")
        self.assertEqual(value_in_range("1035", value_min="1K"), "1035")
        self.assertEqual(
            value_in_range("60000M", value_min="1K", value_max="50G"),
            "50G",
        )
        self.assertEqual(
            value_in_range("60000", value_min="1K", value_max="50G"),
            "50G",
        )
        self.assertEqual(
            value_in_range("60000M", value_min="1K", value_max="70G"),
            "60000M",
        )
        self.assertEqual(
            value_in_range(60000, value_min="1K", value_max="70G"),
            60000,
        )
        self.assertEqual(
            value_in_range(90000 * 1024**2, value_min="1K", value_max="70G"),
            "70G",
        )
        self.assertEqual(
            value_in_range("90000", value_min="1K", value_max="70G"),
            "70G",
        )
        self.assertEqual(
            value_in_range("60000M", value_min="60G", value_max="70G"),
            "60G",
        )

    def test_check_queue_parameters(self):
        cores, run_time_max, memory_max = check_queue_parameters(
            active_queue={"cores_min": 1, "cores_max": 100, "memory_max": 12, "run_time_max": 1000},
            cores=1,
            run_time_max=100,
            memory_max=10,
        )
        self.assertEqual(cores, 1)
        self.assertEqual(run_time_max, 100)
        self.assertEqual(memory_max, 10)