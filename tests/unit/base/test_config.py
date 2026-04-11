import unittest
import sys
from unittest.mock import patch

try:
    import pydantic

    skip_pydantic_test = False
except ImportError:
    skip_pydantic_test = True


class TestConfig(unittest.TestCase):
    def test_bad_queue_type(self):
        from pysqa.base.config import QueueAdapterWithConfig

        with self.assertRaises(ValueError):
            QueueAdapterWithConfig(config={"queue_type": "error", "queues": {}})

    @unittest.skipIf(skip_pydantic_test, "pydantic not installed")
    def test_pydantic_validation_missing_queues(self):
        from pysqa.base.config import QueueAdapterWithConfig

        with self.assertRaises(ValueError):
            QueueAdapterWithConfig(config={"queue_type": "SLURM"})

    @unittest.skipIf(skip_pydantic_test, "pydantic not installed")
    def test_pydantic_validation_wrong_type(self):
        from pysqa.base.config import QueueAdapterWithConfig

        with self.assertRaises(ValueError):
            QueueAdapterWithConfig(
                config={
                    "queue_type": "SLURM",
                    "queues": {"sq": {"script": "slurm.sh", "cores_min": "not_an_int"}},
                }
            )

    def test_pydantic_validation_extra_fields(self):
        from pysqa.base.config import QueueAdapterWithConfig

        config = {
            "queue_type": "SLURM",
            "queue_primary": "sq",
            "queues": {"sq": {"extra_field": "allowed"}},
            "extra_top_level": "also_allowed",
        }
        qa = QueueAdapterWithConfig(config=config)
        self.assertEqual(qa.config["queues"]["sq"]["extra_field"], "allowed")
        self.assertEqual(qa.config["extra_top_level"], "also_allowed")

    def test_no_pydantic_validation_extra_fields(self):
        with patch.dict('sys.modules', {'pydantic': None}):
            if 'pysqa.base.models' in sys.modules:
                del sys.modules['pysqa.base.models']

            if 'pysqa.base.config' in sys.modules:
                del sys.modules['pysqa.base.config']

            from pysqa.base.config import QueueAdapterWithConfig

            config = {
                "queue_type": "SLURM",
                "queue_primary": "sq",
                "queues": {"sq": {"extra_field": "allowed"}},
                "extra_top_level": "also_allowed",
            }
            qa = QueueAdapterWithConfig(config=config)
            self.assertEqual(qa.config["queues"]["sq"]["extra_field"], "allowed")
            self.assertEqual(qa.config["extra_top_level"], "also_allowed")
