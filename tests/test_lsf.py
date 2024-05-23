# coding: utf-8
# Copyright (c) Jan Janssen

import os
import unittest

import pandas

from pysqa import QueueAdapter

__author__ = "Jan Janssen"
__copyright__ = "Copyright 2019, Jan Janssen"
__version__ = "0.0.1"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "production"
__date__ = "Feb 9, 2019"


class TestLsfQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.lsf = QueueAdapter(directory=os.path.join(cls.path, "config/lsf"))

    def test_config(self):
        self.assertEqual(self.lsf.config["queue_type"], "LSF")
        self.assertEqual(self.lsf.config["queue_primary"], "lsf")

    def test_list_clusters(self):
        self.assertEqual(self.lsf.list_clusters(), ["default"])

    def test_ssh_delete_file_on_remote(self):
        self.assertEqual(self.lsf.ssh_delete_file_on_remote, True)

    def test_job_submission_template(self):
        template = (
            "#!/bin/bash\n#BSUB -q queue\n#BSUB -J job.py\n#BSUB -o time.out\n#BSUB -n 10\n#BSUB -cwd .\n"
            "#BSUB -e error.out\n#BSUB -W 259200\n\npython test.py"
        )
        self.assertEqual(
            self.lsf._adapter._job_submission_template(command="python test.py"),
            template,
        )

    def test_interfaces(self):
        self.assertEqual(self.lsf._adapter._commands.submit_job_command, ["bsub"])
        self.assertEqual(self.lsf._adapter._commands.delete_job_command, ["bkill"])
        self.assertEqual(
            self.lsf._adapter._commands.get_queue_status_command, ["bjobs"]
        )

    def test__list_command_to_be_executed(self):
        with self.subTest("lsf"):
            self.assertEqual(
                self.lsf._adapter._list_command_to_be_executed("here"),
                ["bsub", "here"],
            )
        with self.subTest("lsf with dependency"):
            self.assertRaises(
                TypeError,
                self.lsf._adapter._list_command_to_be_executed,
                [],
                "here",
            )

    def test_convert_queue_status_sge(self):
        with open(os.path.join(self.path, "config/lsf", "bjobs_output"), "r") as f:
            content = f.read()
        df = pandas.DataFrame(
            {
                "jobid": [5136563, 5136570, 5136571],
                "user": ["testuse"] * 3,
                "jobname": ["pi_None"] * 3,
                "status": ["running"] * 3,
            }
        )
        self.assertTrue(
            df.equals(
                self.lsf._adapter._commands.convert_queue_status(
                    queue_status_output=content
                )
            )
        )
