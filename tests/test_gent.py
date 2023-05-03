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


class TestGentQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.gent = QueueAdapter(directory=os.path.join(cls.path, "config/gent"))

    def test_config(self):
        self.assertEqual(self.gent.config["queue_type"], "GENT")
        self.assertEqual(self.gent.config["queue_primary"], "slurm")

    def test_list_clusters(self):
        self.assertEqual(self.gent.list_clusters(), ['default'])

    def test_ssh_delete_file_on_remote(self):
        self.assertEqual(self.gent.ssh_delete_file_on_remote, True)

    def test_interfaces(self):
        self.assertEqual(
            self.gent._adapter._commands.get_queue_status_command,
            ["squeue", "--format", "%A|%u|%t|%.15j|%Z", "--noheader"],
        )

    def test__list_command_to_be_executed(self):
        with self.subTest("gent"):
            self.assertEqual(
                self.gent._adapter._list_command_to_be_executed(None, "here"),
                ["sbatch", "--parsable", "here"],
            )
        with self.subTest("gent with dependency"):
            self.assertRaises(
                NotImplementedError,
                self.gent._adapter._list_command_to_be_executed,
                [],
                "here",
            )
