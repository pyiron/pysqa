import unittest

from pysqa.base.modular import ModularQueueAdapter

try:
    import defusedxml.ElementTree as ETree

    skip_sge_test = False
except ImportError:
    skip_sge_test = True


def _stub_execute_command(value):
    def execute_command(
        commands,
        working_directory=None,
        split_output=True,
        shell=False,
        error_filename="pysqa.err",
    ):
        return value

    return execute_command


class TestModularQueueAdapter(unittest.TestCase):
    @unittest.skipIf(
        skip_sge_test,
        "defusedxml is not installed, so the sun grid engine (SGE) tests are skipped.",
    )
    def test_unknown_cluster_raises_value_error(self):
        config = {
            "queue_type": "SGE",
            "queue_primary": "sge",
            "cluster": ["clusterA"],
            "queues": {
                "sge": {
                    "cluster": "clusterB",
                    "cores_max": 100,
                    "cores_min": 1,
                    "run_time_max": 1000,
                }
            },
        }
        with self.assertRaises(ValueError) as context:
            ModularQueueAdapter(config=config, directory=".")
        self.assertIn("clusterB", str(context.exception))

    @unittest.skipIf(
        skip_sge_test,
        "defusedxml is not installed, so the sun grid engine (SGE) tests are skipped.",
    )
    def test_enable_reservation(self):
        config = {
            "queue_type": "SGE",
            "queue_primary": "sge",
            "cluster": ["clusterA"],
            "queues": {
                "sge": {
                    "cluster": "clusterA",
                    "cores_max": 100,
                    "cores_min": 1,
                    "run_time_max": 1000,
                }
            },
        }
        qa = ModularQueueAdapter(
            config=config,
            directory=".",
            execute_command=_stub_execute_command(["Reservation enabled", ""]),
        )
        self.assertEqual(qa.enable_reservation(process_id=10), "Reservation enabled")

    @unittest.skipIf(
        skip_sge_test,
        "defusedxml is not installed, so the sun grid engine (SGE) tests are skipped.",
    )
    def test_enable_reservation_no_output(self):
        config = {
            "queue_type": "SGE",
            "queue_primary": "sge",
            "cluster": ["clusterA"],
            "queues": {
                "sge": {
                    "cluster": "clusterA",
                    "cores_max": 100,
                    "cores_min": 1,
                    "run_time_max": 1000,
                }
            },
        }
        qa = ModularQueueAdapter(
            config=config, directory=".", execute_command=_stub_execute_command(None)
        )
        self.assertIsNone(qa.enable_reservation(process_id=10))

    def test_get_queue_status_no_commands(self):
        # The "REMOTE" queue type has no associated scheduler commands class,
        # so get_queue_status() short-circuits to None.
        config = {
            "queue_type": "REMOTE",
            "queue_primary": "remote",
            "cluster": ["clusterA"],
            "queues": {
                "remote": {
                    "cluster": "clusterA",
                    "cores_max": 100,
                    "cores_min": 1,
                    "run_time_max": 1000,
                }
            },
        }
        qa = ModularQueueAdapter(config=config, directory=".")
        self.assertIsNone(qa.get_queue_status())
