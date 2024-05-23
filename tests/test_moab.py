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


class TestMoabQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.moab = QueueAdapter(directory=os.path.join(cls.path, "config/moab"))

    def test_config(self):
        self.assertEqual(self.moab.config["queue_type"], "MOAB")
        self.assertEqual(self.moab.config["queue_primary"], "moab")

    def test_list_clusters(self):
        self.assertEqual(self.moab.list_clusters(), ["default"])

    def test_ssh_delete_file_on_remote(self):
        self.assertEqual(self.moab.ssh_delete_file_on_remote, True)

    def test_interfaces(self):
        self.assertEqual(self.moab._adapter._commands.submit_job_command, ["msub"])
        self.assertEqual(
            self.moab._adapter._commands.delete_job_command, ["mjobctl", "-c"]
        )
        self.assertEqual(
            self.moab._adapter._commands.get_queue_status_command, ["mdiag", "-x"]
        )

    def test__list_command_to_be_executed(self):
        with self.subTest("moab with dependency"):
            self.assertRaises(
                TypeError,
                self.moab._adapter._list_command_to_be_executed,
                [],
                "here",
            )
        with self.subTest("moab"):
            self.assertEqual(
                self.moab._adapter._list_command_to_be_executed("here"),
                ["msub", "here"],
            )
