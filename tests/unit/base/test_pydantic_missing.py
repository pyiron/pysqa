import unittest
from unittest.mock import patch
import sys
import importlib

class TestPydanticMissing(unittest.TestCase):
    def test_pydantic_missing_fallback(self):
        # Mock sys.modules to simulate pydantic missing
        with patch.dict(sys.modules, {'pydantic': None}):
            # Reload pysqa.base.config to trigger the fallback validate_config
            # but before that we need to reload pysqa.base.models since it is imported in config.py
            if 'pysqa.base.models' in sys.modules:
                importlib.reload(sys.modules['pysqa.base.models'])

            import pysqa.base.config
            importlib.reload(pysqa.base.config)

            from pysqa.base.config import QueueAdapterWithConfig

            config = {
                "queue_type": "SLURM",
                "queues": {"sq": {"cores_min": 1}}
            }
            # This should not raise an error even though it might be invalid for pydantic
            # (missing some required fields if any, though here it is mostly about the fallback)
            qa = QueueAdapterWithConfig(config=config)
            self.assertEqual(qa.config["queue_type"], "SLURM")
            self.assertEqual(qa.config["queues"]["sq"]["cores_min"], 1)

    @classmethod
    def tearDownClass(cls):
        # Restore the state for other tests
        if 'pysqa.base.models' in sys.modules:
            importlib.reload(sys.modules['pysqa.base.models'])
        if 'pysqa.base.config' in sys.modules:
            importlib.reload(sys.modules['pysqa.base.config'])
