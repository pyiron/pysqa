# coding: utf-8
# Copyright (c) Jan Janssen

import os
import pandas
import unittest
import getpass
from pysqa import QueueAdapter
from pysqa.utils.basic import BasisQueueAdapter

__author__ = "Jan Janssen"
__copyright__ = "Copyright 2019, Jan Janssen"
__version__ = "0.0.1"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "production"
__date__ = "Feb 9, 2019"


class TestRunmode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.torque = QueueAdapter(directory=os.path.join(cls.path, "config/torque"))
        cls.slurm = QueueAdapter(directory=os.path.join(cls.path, "config/slurm"))
        cls.lsf = QueueAdapter(directory=os.path.join(cls.path, "config/lsf"))
        cls.sge = QueueAdapter(directory=os.path.join(cls.path, "config/sge"))
        cls.moab = QueueAdapter(directory=os.path.join(cls.path, "config/moab"))
        cls.gent = QueueAdapter(directory=os.path.join(cls.path, "config/gent"))

    def test_missing_config(self):
        self.assertRaises(
            ValueError, QueueAdapter, directory=os.path.join(self.path, "config/error")
        )

    def test_config(self):
        self.assertEqual(self.torque.config["queue_type"], "TORQUE")
        self.assertEqual(self.slurm.config["queue_type"], "SLURM")
        self.assertEqual(self.lsf.config["queue_type"], "LSF")
        self.assertEqual(self.sge.config["queue_type"], "SGE")
        self.assertEqual(self.moab.config["queue_type"], "MOAB")
        self.assertEqual(self.torque.config["queue_primary"], "torque")
        self.assertEqual(self.slurm.config["queue_primary"], "slurm")
        self.assertEqual(self.lsf.config["queue_primary"], "lsf")
        self.assertEqual(self.sge.config["queue_primary"], "impi_hydra_small")
        self.assertEqual(self.moab.config["queue_primary"], "moab")
        self.assertEqual(self.gent.config["queue_primary"], "slurm")

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
        template = (
            "#!/bin/bash\n#BSUB -q queue\n#BSUB -J job.py\n#BSUB -o time.out\n#BSUB -n 10\n#BSUB -cwd .\n"
            "#BSUB -e error.out\n#BSUB -W 259200\n\npython test.py"
        )
        self.assertEqual(
            self.lsf._adapter._job_submission_template(command="python test.py"),
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
        self.assertEqual(
            self.torque._adapter._commands.submit_job_command, ["qsub", "-terse"]
        )
        self.assertEqual(self.torque._adapter._commands.delete_job_command, ["qdel"])
        self.assertEqual(
            self.torque._adapter._commands.get_queue_status_command, ["qstat", "-x"]
        )
        self.assertEqual(
            self.lsf._adapter._commands.submit_job_command, ["bsub", "-terse"]
        )
        self.assertEqual(self.lsf._adapter._commands.delete_job_command, ["bkill"])
        self.assertEqual(
            self.lsf._adapter._commands.get_queue_status_command, ["qstat", "-x"]
        )
        self.assertEqual(
            self.slurm._adapter._commands.submit_job_command, ["sbatch", "--parsable"]
        )
        self.assertEqual(self.slurm._adapter._commands.delete_job_command, ["scancel"])
        self.assertEqual(
            self.slurm._adapter._commands.get_queue_status_command,
            ["squeue", "--format", "%A|%u|%t|%.15j", "--noheader"],
        )
        self.assertEqual(self.moab._adapter._commands.submit_job_command, ["msub"])
        self.assertEqual(
            self.moab._adapter._commands.delete_job_command, ["mjobctl", "-c"]
        )
        self.assertEqual(
            self.moab._adapter._commands.get_queue_status_command, ["mdiag", "-x"]
        )
        self.assertEqual(
            self.gent._adapter._commands.get_queue_status_command,
            ["squeue", "--format", "%A|%u|%t|%j", "--noheader"],
        )

    def test_convert_queue_status(self):
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
        df_merge = df_running.append(df_pending, sort=True)
        df = pandas.DataFrame(
            {
                "jobid": pandas.to_numeric(df_merge.jobid),
                "user": df_merge.user,
                "jobname": df_merge.jobname,
                "status": df_merge.status,
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

    def test_queue_view(self):
        self.assertIsInstance(self.slurm.queue_view, pandas.DataFrame)

    def test_memory_string_comparison(self):
        self.assertEqual(BasisQueueAdapter._value_in_range(1023, value_min="1K"), "1K")
        self.assertEqual(BasisQueueAdapter._value_in_range(1035, value_min="1K"), 1035)
        self.assertEqual(BasisQueueAdapter._value_in_range(1035, value_max="1K"), "1K")
        self.assertEqual(
            BasisQueueAdapter._value_in_range("1035", value_min="1K"), "1035"
        )
        self.assertEqual(
            BasisQueueAdapter._value_in_range(
                "60000M", value_min="1K", value_max="50G"
            ),
            "50G",
        )
        self.assertEqual(
            BasisQueueAdapter._value_in_range("60000", value_min="1K", value_max="50G"),
            "50G",
        )
        self.assertEqual(
            BasisQueueAdapter._value_in_range(
                "60000M", value_min="1K", value_max="70G"
            ),
            "60000M",
        )
        self.assertEqual(
            BasisQueueAdapter._value_in_range(60000, value_min="1K", value_max="70G"),
            60000,
        )
        self.assertEqual(
            BasisQueueAdapter._value_in_range(
                90000 * 1024 ** 2, value_min="1K", value_max="70G"
            ),
            "70G",
        )
        self.assertEqual(
            BasisQueueAdapter._value_in_range("90000", value_min="1K", value_max="70G"),
            "70G",
        )
        self.assertEqual(
            BasisQueueAdapter._value_in_range(
                "60000M", value_min="60G", value_max="70G"
            ),
            "60G",
        )
