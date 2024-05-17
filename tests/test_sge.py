# coding: utf-8
# Copyright (c) Jan Janssen

import os
import pandas
import unittest
import getpass
from pysqa import QueueAdapter

try:
    import defusedxml.ElementTree as ETree

    skip_sge_test = False
except ImportError:
    skip_sge_test = True

__author__ = "Jan Janssen"
__copyright__ = "Copyright 2019, Jan Janssen"
__version__ = "0.0.1"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "production"
__date__ = "Feb 9, 2019"


@unittest.skipIf(
    skip_sge_test,
    "defusedxml is not installed, so the sun grid engine (SGE) tests are skipped.",
)
class TestSGEQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.sge = QueueAdapter(directory=os.path.join(cls.path, "config/sge"))

    def test_config(self):
        self.assertEqual(self.sge.config["queue_type"], "SGE")
        self.assertEqual(self.sge.config["queue_primary"], "impi_hydra_small")

    def test_list_clusters(self):
        self.assertEqual(self.sge.list_clusters(), ["default"])

    def test_ssh_delete_file_on_remote(self):
        self.assertEqual(self.sge.ssh_delete_file_on_remote, True)

    def test_value_in_range(self):
        self.assertEqual(
            None,
            self.sge._adapter._value_in_range(
                value=None, value_min=None, value_max=None
            ),
        )
        self.assertEqual(
            1,
            self.sge._adapter._value_in_range(value=None, value_min=1, value_max=None),
        )
        self.assertEqual(
            1,
            self.sge._adapter._value_in_range(value=None, value_min=None, value_max=1),
        )
        self.assertEqual(
            1,
            self.sge._adapter._value_in_range(value=1, value_min=None, value_max=None),
        )
        self.assertEqual(
            1, self.sge._adapter._value_in_range(value=0, value_min=1, value_max=None)
        )
        self.assertEqual(
            1, self.sge._adapter._value_in_range(value=2, value_min=None, value_max=1)
        )
        self.assertEqual(
            1, self.sge._adapter._value_in_range(value=1, value_min=0, value_max=2)
        )

    def test_job_submission_template(self):
        self.assertRaises(
            ValueError, self.sge._adapter._job_submission_template, command=None
        )
        self.assertRaises(
            TypeError, self.sge._adapter._job_submission_template, command=1
        )
        template = (
            "#!/bin/bash\n#$ -N job.py\n#$ -wd .\n#$ -pe impi_hydra_small 1\n#$ -l h_rt=604800\n"
            "#$ -o time.out\n#$ -e error.out\n\npython test.py"
        )
        self.assertEqual(
            self.sge._adapter._job_submission_template(command="python test.py"),
            template,
        )
        self.assertRaises(
            ValueError,
            self.sge._adapter._job_submission_template,
            command="python test.py",
            queue="notavailable",
        )

    def test_interfaces(self):
        self.assertEqual(
            self.sge._adapter._commands.submit_job_command, ["qsub", "-terse"]
        )
        self.assertEqual(self.sge._adapter._commands.delete_job_command, ["qdel"])
        self.assertEqual(
            self.sge._adapter._commands.enable_reservation_command,
            ["qalter", "-R", "y"],
        )
        self.assertEqual(
            self.sge._adapter._commands.get_queue_status_command, ["qstat", "-xml"]
        )

    def test__list_command_to_be_executed(self):
        with self.subTest("sge"):
            self.assertEqual(
                self.sge._adapter._list_command_to_be_executed("here"),
                ["qsub", "-terse", "here"],
            )
        with self.subTest("sge with dependency"):
            self.assertRaises(
                TypeError,
                self.sge._adapter._list_command_to_be_executed,
                [],
                "here",
            )

    def test_convert_queue_status_sge(self):
        with open(os.path.join(self.path, "config/sge", "qstat.xml"), "r") as f:
            content = f.read()
        df_running = pandas.DataFrame(
            {
                "jobid": ["2836045"],
                "user": ["friko"],
                "jobname": ["vasp.5.3.5"],
                "status": ["running"],
            }
        )
        df_pending = pandas.DataFrame(
            {
                "jobid": ["2836046", "2967274"],
                "user": ["friko", "janj"],
                "jobname": ["vasp.5.3.5", "hello.py"],
                "status": ["pending", "error"],
            }
        )
        df_merge = pandas.concat([df_running, df_pending], sort=True)
        df = pandas.DataFrame(
            {
                "jobid": pandas.to_numeric(df_merge.jobid),
                "user": df_merge.user,
                "jobname": df_merge.jobname,
                "status": df_merge.status,
                "working_directory": [""] * len(df_merge),
            }
        )
        self.assertTrue(
            df.equals(
                self.sge._adapter._commands.convert_queue_status(
                    queue_status_output=content
                )
            )
        )

    def test_queue_list(self):
        self.assertEqual(
            sorted(self.sge.queue_list),
            ["impi_hy", "impi_hydra", "impi_hydra_cmfe", "impi_hydra_small"],
        )

    def test_queues(self):
        self.assertEqual(self.sge.queues.impi_hydra, "impi_hydra")
        self.assertEqual(
            sorted(dir(self.sge.queues)),
            ["impi_hy", "impi_hydra", "impi_hydra_cmfe", "impi_hydra_small"],
        )
        with self.assertRaises(AttributeError):
            _ = self.sge.queues.notavailable

    def test_get_user(self):
        self.assertEqual(self.sge._adapter._get_user(), getpass.getuser())

    def test_check_queue_parameters(self):
        self.assertEqual(
            (1, 604800, None), self.sge.check_queue_parameters(queue="impi_hydra_small")
        )
