import unittest
import sys
from unittest.mock import patch


class TestPydanticModels(unittest.TestCase):
    def test_no_pydantic_validation_extra_fields(self):
        with patch.dict('sys.modules', {'pydantic': None}):
            if 'pysqa.base.models' in sys.modules:
                del sys.modules['pysqa.base.models']

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
