# coding: utf-8
# Copyright (c) Jan Janssen

import os
import pandas
import unittest
import getpass
from pysqa import QueueAdapter

__author__ = "Jan Janssen"
__copyright__ = "Copyright 2019, Jan Janssen"
__version__ = "0.0.1"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "production"
__date__ = "Feb 9, 2019"


df_queue_status = pandas.DataFrame(
    {
        "jobid": [5322019, 5322016, 5322017, 5322018, 5322013],
        "user": ["janj", "janj", "janj", "janj", "maxi"],
        "jobname": [
            "pi_19576488",
            "pi_19576485",
            "pi_19576486",
            "pi_19576487",
            "pi_19576482",
        ],
        "status": ["running", "running", "running", "running", "running"],
        "working_directory": [
            "/cmmc/u/janj/pyiron/projects/2023/2023-04-19-dft-test/job_1",
            "/cmmc/u/janj/pyiron/projects/2023/2023-04-19-dft-test/job_2",
            "/cmmc/u/janj/pyiron/projects/2023/2023-04-19-dft-test/job_3",
            "/cmmc/u/janj/pyiron/projects/2023/2023-04-19-dft-test/job_4",
            "/cmmc/u/janj/pyiron/projects/2023/2023-04-19-dft-test/job_5",
        ],
    }
)


class TestSlurmQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.slurm = QueueAdapter(directory=os.path.join(cls.path, "config/slurm"))

    def test_config(self):
        self.assertEqual(self.slurm.config["queue_type"], "SLURM")
        self.assertEqual(self.slurm.config["queue_primary"], "slurm")

    def test_list_clusters(self):
        self.assertEqual(self.slurm.list_clusters(), ["default"])

    def test_remote_flag(self):
        self.assertFalse(self.slurm._adapter.remote_flag)

    def test_ssh_delete_file_on_remote(self):
        self.assertEqual(self.slurm.ssh_delete_file_on_remote, True)

    def test_interfaces(self):
        self.assertEqual(
            self.slurm._adapter._commands.submit_job_command, ["sbatch", "--parsable"]
        )
        self.assertEqual(self.slurm._adapter._commands.delete_job_command, ["scancel"])
        self.assertEqual(
            self.slurm._adapter._commands.get_queue_status_command,
            ["squeue", "--format", "%A|%u|%t|%.15j|%Z", "--noheader"],
        )

    def test__list_command_to_be_executed(self):
        with self.subTest("slurm"):
            self.assertEqual(
                self.slurm._adapter._list_command_to_be_executed("here"),
                ["sbatch", "--parsable", "here"],
            )

    def test_convert_queue_status_slurm(self):
        with open(os.path.join(self.path, "config/slurm", "squeue_output"), "r") as f:
            content = f.read()
        self.assertTrue(
            df_queue_status.equals(
                self.slurm._adapter._commands.convert_queue_status(
                    queue_status_output=content
                )
            )
        )

    def test_get_user(self):
        self.assertEqual(self.slurm._adapter._get_user(), getpass.getuser())

    def test_queue_view(self):
        self.assertIsInstance(self.slurm.queue_view, pandas.DataFrame)

    def test_submit_job_empty_working_directory(self):
        with self.assertRaises(ValueError):
            self.slurm.submit_job(working_directory=" ")

    def test_write_queue(self):
        with self.assertRaises(ValueError):
            self.slurm._adapter._write_queue_script(
                queue=None,
                job_name=None,
                working_directory=None,
                cores=None,
                memory_max=None,
                run_time_max=None,
                command=None,
            )
        self.slurm._adapter._write_queue_script(
            queue="slurm",
            job_name=None,
            working_directory=None,
            cores=None,
            memory_max=None,
            run_time_max=None,
            command='echo "hello"',
        )
        with open("run_queue.sh", "r") as f:
            content = f.read()
        output = """\
#!/bin/bash
#SBATCH --output=time.out
#SBATCH --job-name=None
#SBATCH --chdir=.
#SBATCH --get-user-env=L
#SBATCH --partition=slurm
#SBATCH --time=4320
#SBATCH --cpus-per-task=10

echo \"hello\""""
        self.assertEqual(content, output)
        os.remove("run_queue.sh")

    def test_write_queue_extra_keywords(self):
        self.slurm._adapter._write_queue_script(
            queue="slurm_extra",
            job_name=None,
            working_directory=None,
            cores=None,
            memory_max=None,
            run_time_max=None,
            command='echo "hello"',
            account="123456",
        )
        with open("run_queue.sh", "r") as f:
            content = f.read()
        output = """\
#!/bin/bash
#SBATCH --output=time.out
#SBATCH --job-name=None
#SBATCH --chdir=.
#SBATCH --get-user-env=L
#SBATCH --partition=slurm
#SBATCH --account=123456
#SBATCH --time=4320
#SBATCH --cpus-per-task=10

echo \"hello\""""
        self.assertEqual(content, output)
        os.remove("run_queue.sh")

    def test_no_queue_id_returned(self):
        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            pass

        slurm_tmp = QueueAdapter(
            directory=os.path.join(self.path, "config/slurm"),
            execute_command=execute_command,
        )
        self.assertIsNone(
            slurm_tmp.submit_job(
                queue="slurm",
                job_name="test",
                working_directory=".",
                command="echo hello",
            )
        )
        self.assertIsNone(slurm_tmp.delete_job(process_id=123))

    def test_queue_status(self):
        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            with open(os.path.join(self.path, "config", "slurm", "squeue_output")) as f:
                return f.read()

        slurm_tmp = QueueAdapter(
            directory=os.path.join(self.path, "config/slurm"),
            execute_command=execute_command,
        )
        self.assertTrue(df_queue_status.equals(slurm_tmp.get_queue_status()))
        self.assertTrue(
            df_queue_status[df_queue_status.user == "janj"].equals(
                slurm_tmp.get_queue_status(user="janj")
            )
        )
        self.assertEqual(slurm_tmp.get_status_of_job(process_id=5322019), "running")
        self.assertIsNone(slurm_tmp.get_status_of_job(process_id=0))
        self.assertEqual(
            slurm_tmp.get_status_of_jobs(process_id_lst=[5322019, 0]),
            ["running", "finished"],
        )

    def test_not_implemented_functions(self):
        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            pass

        slurm_tmp = QueueAdapter(
            directory=os.path.join(self.path, "config/slurm"),
            execute_command=execute_command,
        )

        with self.assertRaises(NotImplementedError):
            slurm_tmp._adapter.convert_path_to_remote(path="test")

        with self.assertRaises(NotImplementedError):
            slurm_tmp._adapter.transfer_file(
                file="test", transfer_back=False, delete_file_on_remote=False
            )

        with self.assertRaises(NotImplementedError):
            slurm_tmp._adapter.get_job_from_remote(working_directory=".")
