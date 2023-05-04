# coding: utf-8
# Copyright (c) Jan Janssen

import os
import unittest
from pysqa import QueueAdapter


try:
    import flux
    skip_flux_test = False
except ImportError:
    skip_flux_test = True


@unittest.skipIf(skip_flux_test, "Flux is not installed, so the flux tests are skipped")
class TestFluxQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
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
        print(self.flux._adapter._commands.convert_queue_status(
                    queue_status_output=content
        ))
