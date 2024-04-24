# coding: utf-8
# Copyright (c) Jan Janssen

import os
import unittest

import pandas
from pysqa import QueueAdapter
from pysqa.executor.executor import Executor


try:
    import flux
    skip_flux_test = False
except ImportError:
    skip_flux_test = True


def funct_add(a, b):
    return a+b


@unittest.skipIf(skip_flux_test, "Flux is not installed, so the flux tests are skipped.")
class TestFluxQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.test_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "cache")
        os.makedirs(cls.test_dir, exist_ok=True)
        cls.flux = QueueAdapter(directory=os.path.join(cls.path, "config/flux"))

    def test_config(self):
        self.assertEqual(self.flux.config["queue_type"], "FLUX")
        self.assertEqual(self.flux.config["queue_primary"], "flux")

    def test_list_clusters(self):
        self.assertEqual(self.flux.list_clusters(), ['default'])

    def test_remote_flag(self):
        self.assertFalse(self.flux._adapter.remote_flag)

    def test_ssh_delete_file_on_remote(self):
        self.assertEqual(self.flux.ssh_delete_file_on_remote, True)

    def test_interfaces(self):
        self.assertEqual(
            self.flux._adapter._commands.submit_job_command, ["flux", "batch"]
        )
        self.assertEqual(self.flux._adapter._commands.delete_job_command, ["flux", "cancel"])
        self.assertEqual(
            self.flux._adapter._commands.get_queue_status_command,
            ["flux", "jobs", "-a", "--no-header"],
        )

    def test_convert_queue_status_slurm(self):
        with open(os.path.join(self.path, "config/flux", "flux_jobs"), "r") as f:
            content = f.read()
        df = pandas.DataFrame({
            "jobid": [1125147213824, 1109007532032, 1092532305920],
            "user": ["dahn", "dahn", "dahn"],
            "jobname": ["sleep_batc", "sleep_batc", "sleep_batc"],
            "status": ["running", "running", "running"]
        })
        self.assertTrue(df.equals(self.flux._adapter._commands.convert_queue_status(
            queue_status_output=content
        )))

    def test_submit_job(self):
        def execute_command(
                commands,
                working_directory=None,
                split_output=True,
                shell=False,
                error_filename="pysqa.err",
        ):
            return "ƒWZEQa8X\n"

        flux_tmp = QueueAdapter(
            directory=os.path.join(self.path, "config/flux"),
            execute_command=execute_command
        )
        self.assertEqual(flux_tmp.submit_job(
            queue="flux",
            job_name="test",
            working_directory=".",
            cores=4,
            command="echo hello"
        ), 1125147213824)
        with open("run_queue.sh") as f:
            output = f.read()
        content = """\
#!/bin/bash
# flux:--job-name=test
# flux: --env=CORES=4
# flux: --output=time.out
# flux: --error=error.out
# flux: -n 4
# flux: -t 2880

echo hello"""
        self.assertEqual(content, output)
        os.remove("run_queue.sh")

    def test_flux_integration(self):
        job_id = self.flux.submit_job(
            queue="flux",
            job_name="test",
            working_directory=".",
            cores=1,
            command="sleep 1"
        )
        self.assertEqual(self.flux.get_status_of_job(process_id=job_id), 'running')
        self.flux.delete_job(process_id=job_id)
        self.assertEqual(self.flux.get_status_of_job(process_id=job_id), 'error')

    def test_executor_integration(self):
        with Executor(
            cwd=self.test_dir,
            queue_adapter=self.flux,
            queue_adapter_kwargs={
                "queue": "flux",
                "job_name": "test",
                "cores": 1,
            }
        ) as exe:
            fs = exe.submit(fn=funct_add, a=1, b=2)
            self.assertFalse(fs.done())
            self.assertEqual(fs.result(), 3)
            self.assertTrue(fs.done())
