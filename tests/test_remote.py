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

    def test_config(self):
        self.assertEqual(self.remote.config["queue_type"], "REMOTE")
        self.assertEqual(self.remote.config["queue_primary"], "remote")

    def test_list_clusters(self):
        self.assertEqual(self.remote.list_clusters(), ['default'])

    def test_ssh_delete_file_on_remote(self):
        self.assertEqual(self.remote.ssh_delete_file_on_remote, False)

    def test_submit_job_remote(self):
        with self.assertRaises(NotImplementedError):
            self.remote.submit_job(queue="remote", dependency_list=[])
