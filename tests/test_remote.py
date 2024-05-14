# coding: utf-8
# Copyright (c) Jan Janssen

import os
import unittest
from pysqa import QueueAdapter

try:
    import paramiko
    from tqdm import tqdm

    skip_remote_test = False
except ImportError:
    skip_remote_test = True


__author__ = "Jan Janssen"
__copyright__ = "Copyright 2019, Jan Janssen"
__version__ = "0.0.1"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "production"
__date__ = "Feb 9, 2019"


@unittest.skipIf(
    skip_remote_test,
    "Either paramiko or tqdm are not installed, so the remote queue adapter tests are skipped.",
)
class TestRemoteQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.remote = QueueAdapter(directory=os.path.join(cls.path, "config/remote"))
        cls.remote_alternative = QueueAdapter(
            directory=os.path.join(cls.path, "config/remote_alternative")
        )

    def test_config(self):
        self.assertEqual(self.remote.config["queue_type"], "REMOTE")
        self.assertEqual(self.remote.config["queue_primary"], "remote")

    def test_list_clusters(self):
        self.assertEqual(self.remote.list_clusters(), ["default"])

    def test_remote_flag(self):
        self.assertTrue(self.remote._adapter.remote_flag)

    def test_ssh_delete_file_on_remote(self):
        self.assertEqual(self.remote.ssh_delete_file_on_remote, False)

    def test_ssh_continous_connection(self):
        self.assertEqual(self.remote._adapter._ssh_continous_connection, True)
        self.assertEqual(
            self.remote_alternative._adapter._ssh_continous_connection, False
        )

    def test_submit_job_remote(self):
        with self.assertRaises(NotImplementedError):
            self.remote.submit_job(queue="remote", dependency_list=[])

    def test_submit_command(self):
        command = self.remote._adapter._submit_command(
            queue="remote",
            job_name="test",
            working_directory="/home/localuser/projects/test",
            cores=str(1),
            memory_max=str(1),
            run_time_max=str(1),
            command_str="/bin/true",
        )
        self.assertEqual(
            command,
            'python -m pysqa --config_directory /u/share/pysqa/resources/queues/ --submit --queue remote --job_name test --working_directory /home/localuser/projects/test --cores 1 --memory 1 --run_time 1 --command "/bin/true" ',
        )

    def test_get_queue_status_command(self):
        command = self.remote._adapter._get_queue_status_command()
        self.assertEqual(
            command,
            "python -m pysqa --config_directory /u/share/pysqa/resources/queues/ --status",
        )

    def test_convert_path_to_remote(self):
        self.assertEqual(
            self.remote.convert_path_to_remote("/home/localuser/projects/test"),
            "/u/hpcuser/remote/test",
        )

    def test_delete_command(self):
        self.assertEqual(
            "python -m pysqa --config_directory /u/share/pysqa/resources/queues/ --delete --id 123",
            self.remote._adapter._delete_command(job_id=123),
        )

    def test_reservation_command(self):
        self.assertEqual(
            "python -m pysqa --config_directory /u/share/pysqa/resources/queues/ --reservation --id 123",
            self.remote._adapter._reservation_command(job_id=123),
        )

    def test_get_ssh_user(self):
        self.assertEqual(self.remote._adapter._get_user(), "hpcuser")

    def test_get_file_transfer(self):
        self.assertEqual(
            self.remote._adapter._get_file_transfer(
                file="abc.txt", local_dir="local", remote_dir="test"
            ),
            os.path.abspath("abc.txt"),
        )
