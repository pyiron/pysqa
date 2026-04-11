import os
import unittest
from jinja2.exceptions import TemplateSyntaxError
from pysqa import QueueAdapter

try:
    import paramiko
    from tqdm import tqdm

    skip_multi_test = False
except ImportError:
    skip_multi_test = True


class TestQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))

    def test_missing_config(self):
        with self.assertRaises(ValueError):
            QueueAdapter(directory=os.path.join(self.path, "../static/error"))

    def test_missing_config_folder(self):
        with self.assertRaises(ValueError):
            QueueAdapter(directory=os.path.join(self.path, "../static"))

    def test_no_config(self):
        with self.assertRaises(ValueError):
            QueueAdapter()

    def test_bad_queue_template(self):
        with self.assertRaises(TemplateSyntaxError):
            QueueAdapter(directory=os.path.join(self.path, "../static/bad_template"))


@unittest.skipIf(
    skip_multi_test,
    "Either paramiko or tqdm are not installed, so the multi queue adapter tests are skipped.",
)
class TestMultiQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.multi = QueueAdapter(
            directory=os.path.join(cls.path, "../static/multicluster")
        )

    def test_config(self):
        self.assertEqual(self.multi.config["queue_type"], "SLURM")
        self.assertEqual(self.multi.config["queue_primary"], "slurm")

    def test_list_clusters(self):
        self.assertEqual(self.multi.list_clusters(), ["local_slurm", "remote_slurm"])

    def test_switch_cluster(self):
        self.assertEqual(self.multi.queue_list, ['slurm'])
        self.multi.switch_cluster("local_slurm")
        self.assertEqual(self.multi.queue_list, ['slurm'])
        self.multi.switch_cluster("remote_slurm")
        self.assertEqual(self.multi.queue_list, ['remote'])
        self.multi.switch_cluster("local_slurm")
        self.assertEqual(self.multi.queue_list, ['slurm'])


@unittest.skipIf(
    skip_multi_test,
    "Either paramiko or tqdm are not installed, so the multi queue adapter tests are skipped.",
)
class TestNoneAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.multi = QueueAdapter(
            directory=os.path.join(cls.path, "../static/multicluster")
        )
        cls.multi._adapter = None

    def test_config(self):
        self.assertIsNone(self.multi.config)

    def test_queue_list(self):
        self.assertIsNone(self.multi.queue_list)

    def test_queue_view(self):
        self.assertIsNone(self.multi.queue_view)

    def test_queues(self):
        self.assertIsNone(self.multi.queues)

    def test_get_job_from_remote(self):
        with self.assertRaises(TypeError):
            self.multi.get_job_from_remote(working_directory=".")

    def test_transfer_file_to_remote(self):
        with self.assertRaises(TypeError):
            self.multi.transfer_file_to_remote(file="test.py")

    def test_convert_path_to_remote(self):
        with self.assertRaises(TypeError):
            self.multi.convert_path_to_remote(path=".")

    def test_check_queue_parameters(self):
        cores_input = 1
        run_time_input = 4320 * 60
        cores, run_time_max, memory_max = self.multi.check_queue_parameters(
            queue="test_queue",
            cores=cores_input,
            run_time_max=run_time_input,
        )
        self.assertEqual(cores_input, cores)
        self.assertEqual(run_time_max, run_time_input)
        self.assertIsNone(memory_max)
