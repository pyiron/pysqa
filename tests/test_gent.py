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

df_queue_status = pandas.DataFrame(
    {
        "cluster": ["Mycluster", "Mycluster", "Mycluster", "Mycluster", "Mycluster"],
        "jobid": [5322019, 5322016, 5322017, 5322018, 5322013],
        "user": ["janj", "janj", "janj", "janj", "janj"],
        "jobname": [
            "pi_19576488",
            "pi_19576485",
            "pi_19576486",
            "pi_19576487",
            "pi_19576482",
        ],
        "status": ["r", "r", "r", "r", "r"],
    }
)


class TestGentQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.gent = QueueAdapter(directory=os.path.join(cls.path, "config/gent"))

    def test_config(self):
        self.assertEqual(self.gent.config["queue_type"], "GENT")
        self.assertEqual(self.gent.config["queue_primary"], "slurm")

    def test_list_clusters(self):
        self.assertEqual(self.gent.list_clusters(), ["default"])

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
                self.gent._adapter._list_command_to_be_executed("here"),
                ["sbatch", "--parsable", "here"],
            )
        with self.subTest("gent with dependency"):
            self.assertRaises(
                TypeError,
                self.gent._adapter._list_command_to_be_executed,
                [],
                "here",
            )

    def test_get_job_id_from_output(self):
        self.assertEqual(
            self.gent._adapter._commands.get_job_id_from_output("123;MyQueue"), 123
        )

    def test_get_queue_from_output(self):
        self.assertEqual(
            self.gent._adapter._commands.get_queue_from_output("123;MyQueue"), "MyQueue"
        )

    def test_convert_queue_status_slurm(self):
        with open(os.path.join(self.path, "config/gent", "gent_output"), "r") as f:
            content = f.read()
        self.assertTrue(
            df_queue_status.equals(
                self.gent._adapter._commands.convert_queue_status(
                    queue_status_output=content
                )
            )
        )

    def test_switch_cluster_command(self):
        self.assertEqual(
            self.gent._adapter._switch_cluster_command(cluster_module="module1"),
            ["module", "--quiet", "swap", "cluster/module1;"],
        )

    def test_resolve_queue_id(self):
        self.assertEqual(
            self.gent._adapter._resolve_queue_id(
                process_id=20120, cluster_dict={0: "cluster1"}
            ),
            ("cluster1", 2012),
        )

    def test_submit_job_no_output(self):
        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            pass

        gent_tmp = QueueAdapter(
            directory=os.path.join(self.path, "config/gent"),
            execute_command=execute_command,
        )
        self.assertIsNone(
            gent_tmp.submit_job(
                queue="slurm",
                job_name="test",
                working_directory=".",
                command="echo hello",
            )
        )
        os.remove("run_queue.sh")

    def test_submit_job_with_output(self):
        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            return "123;cluster0"

        gent_tmp = QueueAdapter(
            directory=os.path.join(self.path, "config/gent"),
            execute_command=execute_command,
        )
        self.assertEqual(
            gent_tmp.submit_job(
                queue="slurm",
                job_name="test",
                working_directory=".",
                command="echo hello",
            ),
            1230,
        )
        os.remove("run_queue.sh")

    def test_delete_job_no_output(self):
        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            pass

        gent_tmp = QueueAdapter(
            directory=os.path.join(self.path, "config/gent"),
            execute_command=execute_command,
        )
        self.assertIsNone(gent_tmp.delete_job(process_id=1))

    def test_delete_job_with_output(self):
        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            return 0, 1

        gent_tmp = QueueAdapter(
            directory=os.path.join(self.path, "config/gent"),
            execute_command=execute_command,
        )
        self.assertEqual(gent_tmp.delete_job(process_id=1), 0)

    def test_get_queue_status(self):
        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            with open(os.path.join(self.path, "config", "gent", "gent_output")) as f:
                return f.read()

        gent_tmp = QueueAdapter(
            directory=os.path.join(self.path, "config/gent"),
            execute_command=execute_command,
        )
        self.assertTrue(
            pandas.concat([df_queue_status] * 3)
            .reset_index(drop=True)
            .equals(gent_tmp.get_queue_status())
        )

    def test_get_queue_status_user(self):
        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            with open(os.path.join(self.path, "config", "gent", "gent_output")) as f:
                return f.read()

        gent_tmp = QueueAdapter(
            directory=os.path.join(self.path, "config/gent"),
            execute_command=execute_command,
        )
        self.assertTrue(
            pandas.concat([df_queue_status] * 3)
            .reset_index(drop=True)
            .equals(gent_tmp.get_queue_status(user="janj"))
        )
