# coding: utf-8
# Copyright (c) Jan Janssen

import os
import unittest
from pysqa import QueueAdapter

__author__ = "Jan Janssen"
__copyright__ = "Copyright 2019, Jan Janssen"
__version__ = "0.0.1"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "production"
__date__ = "Feb 9, 2019"


class TestRemoteQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.remote = QueueAdapter(directory=os.path.join(cls.path, "config/remote"))
        cls.remote_alternative = QueueAdapter(directory=os.path.join(cls.path, "config/remote_alternative"))

    def test_config(self):
        self.assertEqual(self.remote.config["queue_type"], "REMOTE")
        self.assertEqual(self.remote.config["queue_primary"], "remote")

    def test_list_clusters(self):
        self.assertEqual(self.remote.list_clusters(), ['default'])

    def test_remote_flag(self):
        self.assertTrue(self.remote._adapter.remote_flag)

    def test_ssh_delete_file_on_remote(self):
        self.assertEqual(self.remote.ssh_delete_file_on_remote, False)

    def test_submit_job_remote(self):
        with self.assertRaises(NotImplementedError):
            self.remote.submit_job(queue="remote", dependency_list=[])

    def test_convert_path_to_remote(self):
        self.assertEqual(self.remote.convert_path_to_remote("/home/localuser/projects/test"), "/u/hpcuser/remote/test")

    def test_delete_command(self):
        self.assertEqual(
            "python -m pysqa.cmd --config_directory /u/share/pysqa/resources/queues/ --delete --id 123",
            self.remote._adapter._delete_command(job_id=123)
        )

    def test_reservation_command(self):
        self.assertEqual(
            "python -m pysqa.cmd --config_directory /u/share/pysqa/resources/queues/ --reservation --id 123",
            self.remote._adapter._reservation_command(job_id=123)
        )

    def test_get_ssh_user(self):
        self.assertEqual(self.remote._adapter._get_user(), "hpcuser")

    def test_get_file_transfer(self):
        self.assertEqual(
            self.remote._adapter._get_file_transfer(file="abc.txt", local_dir="local", remote_dir="test"),
            os.path.abspath("abc.txt")
        )