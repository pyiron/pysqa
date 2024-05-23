# coding: utf-8
# Copyright (c) Jan Janssen

import os
import pandas
import unittest
from pysqa import QueueAdapter

__author__ = "Jan Janssen"
__copyright__ = "Copyright 2019, Jan Janssen"
__version__ = "0.0.1"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "production"
__date__ = "Feb 9, 2019"


class TestTorqueQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.torque = QueueAdapter(directory=os.path.join(cls.path, "config/torque"))

    def test_config(self):
        self.assertEqual(self.torque.config["queue_type"], "TORQUE")
        self.assertEqual(self.torque.config["queue_primary"], "torque")

    def test_list_clusters(self):
        self.assertEqual(self.torque.list_clusters(), ["default"])

    def test_ssh_delete_file_on_remote(self):
        self.assertEqual(self.torque.ssh_delete_file_on_remote, True)

    def test_interfaces(self):
        self.assertEqual(self.torque._adapter._commands.submit_job_command, ["qsub"])
        self.assertEqual(self.torque._adapter._commands.delete_job_command, ["qdel"])
        self.assertEqual(
            self.torque._adapter._commands.get_queue_status_command, ["qstat", "-f"]
        )

    def test__list_command_to_be_executed(self):
        with self.subTest("torque"):
            self.assertEqual(
                self.torque._adapter._list_command_to_be_executed("here"),
                ["qsub", "here"],
            )
        with self.subTest("torque with dependency"):
            self.assertRaises(
                TypeError,
                self.torque._adapter._list_command_to_be_executed,
                [],
                "here",
            )

    def test_convert_queue_status_torque(self):
        with open(
            os.path.join(self.path, "config/torque", "PBSPro_qsub_output"), "r"
        ) as f:
            content = f.read()
        df_verify = pandas.DataFrame(
            {
                "jobid": [80005196, 80005197, 80005198],
                "user": ["asd562", "asd562", "fgh562"],
                "jobname": [
                    "test1",
                    "test2",
                    "test_asdfasdfasdfasdfasdfasdfasdfasdfasdfasdf",
                ],
                "status": ["running", "pending", "pending"],
                "working_directory": [
                    "/scratch/a01/asd562/VASP/test/test1",
                    "/scratch/a01/asd562/VASP/test/test2",
                    "/scratch/a01/fgh562/VASP/test/test_asdfasdfasdfasdfasdfasdfasdfasdfasdfasdf",
                ],
            }
        )
        self.assertTrue(
            df_verify.equals(
                self.torque._adapter._commands.convert_queue_status(
                    queue_status_output=content
                )
            )
        )
