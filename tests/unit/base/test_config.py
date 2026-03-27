import unittest
from pysqa.base.config import QueueAdapterWithConfig

try:
    import pydantic
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


class TestConfig(unittest.TestCase):
    def test_bad_queue_type(self):
        with self.assertRaises(ValueError):
            QueueAdapterWithConfig(config={"queue_type": "error", "queues": {}})

    @unittest.skipIf(not PYDANTIC_AVAILABLE, "Pydantic not installed")
    def test_pydantic_validation_missing_queues(self):
        with self.assertRaises(ValueError):
            QueueAdapterWithConfig(config={"queue_type": "SLURM"})

    @unittest.skipIf(not PYDANTIC_AVAILABLE, "Pydantic not installed")
    def test_pydantic_validation_wrong_type(self):
        with self.assertRaises(ValueError):
            QueueAdapterWithConfig(
                config={
                    "queue_type": "SLURM",
                    "queues": {"sq": {"script": "slurm.sh", "cores_min": "not_an_int"}},
                }
            )

    def test_pydantic_validation_extra_fields(self):
        config = {
            "queue_type": "SLURM",
            "queue_primary": "sq",
            "queues": {"sq": {"extra_field": "allowed"}},
            "extra_top_level": "also_allowed",
        }
        qa = QueueAdapterWithConfig(config=config)
        self.assertEqual(qa.config["queues"]["sq"]["extra_field"], "allowed")
        self.assertEqual(qa.config["extra_top_level"], "also_allowed")
