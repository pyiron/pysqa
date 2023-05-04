# coding: utf-8
from pysqa.wrapper.generic import SchedulerCommands
import subprocess


class FluxCommands(SchedulerCommands):
    @property
    def submit_job_command(self):
        return ["flux", "batch"]

    @property
    def delete_job_command(self):
        return ["flux", "cancel"]

    @property
    def get_queue_status_command(self):
        return ["flux", "jobs", "-a", "--no-header"]

    @staticmethod
    def get_job_id_from_output(queue_submit_output):
        result = subprocess.run(
            ['flux', 'job', 'id', queue_submit_output.splitlines()[-1].rstrip().lstrip().split()[-1]],
            stdout=subprocess.PIPE
        )
        return int(result.stdout.strip())
