# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

from pysqa.wrapper.generic import SchedulerCommands

__author__ = "Jan Janssen"
__copyright__ = (
    "Copyright 2019, Max-Planck-Institut für Eisenforschung GmbH - "
    "Computational Materials Design (CM) Department"
)
__version__ = "1.0"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "development"
__date__ = "Feb 9, 2019"


class MoabCommands(SchedulerCommands):
    @property
    def submit_job_command(self) -> list[str]:
        """
        Get the command to submit a job.

        Returns:
            list[str]: The command to submit a job.
        """
        return ["msub"]

    @property
    def delete_job_command(self) -> list[str]:
        """
        Get the command to delete a job.

        Returns:
            list[str]: The command to delete a job.
        """
        return ["mjobctl", "-c"]

    @property
    def get_queue_status_command(self) -> list[str]:
        """
        Get the command to get the queue status.

        Returns:
            list[str]: The command to get the queue status.
        """
        return ["mdiag", "-x"]
