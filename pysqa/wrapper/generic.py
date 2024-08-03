# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

from abc import ABC, abstractmethod

import pandas

__author__ = "Niklas Siemer"
__copyright__ = (
    "Copyright 2022, Max-Planck-Institut für Eisenforschung GmbH - "
    "Computational Materials Design (CM) Department"
)
__version__ = "1.0"
__maintainer__ = "Niklas Siemer"
__email__ = "siemer@mpie.de"
__status__ = "production"
__date__ = "Aug 15, 2022"


class SchedulerCommands(ABC):
    @property
    @abstractmethod
    def submit_job_command(self) -> list[str]:
        """
        Returns the command to submit a job to the scheduler.

        Returns:
            list[str]: The command to submit a job.
        """
        pass

    @property
    @abstractmethod
    def delete_job_command(self) -> list[str]:
        """
        Returns the command to delete a job from the scheduler.

        Returns:
            list[str]: The command to delete a job.
        """
        pass

    @property
    def enable_reservation_command(self) -> list[str]:
        """
        Returns the command to enable job reservation on the scheduler.

        Returns:
            list[str]: The command to enable job reservation.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def get_queue_status_command(self) -> list[str]:
        """
        Returns the command to get the status of the job queue.

        Returns:
            list[str]: The command to get the queue status.
        """
        pass

    @staticmethod
    def dependencies(dependency_list: list[str]) -> list:
        """
        Returns the list of dependencies for a job.

        Args:
            dependency_list (list[str]): The list of dependencies.

        Returns:
            list: The list of dependencies.
        """
        if dependency_list is not None:
            raise NotImplementedError()
        else:
            return []

    @staticmethod
    def get_job_id_from_output(queue_submit_output: str) -> int:
        """
        Returns the job ID from the output of the job submission command.

        Args:
            queue_submit_output (str): The output of the job submission command.

        Returns:
            int: The job ID.
        """
        raise NotImplementedError()

    @staticmethod
    def convert_queue_status(queue_status_output: str) -> pandas.DataFrame:
        """
        Converts the output of the queue status command to a pandas DataFrame.

        Args:
            queue_status_output (str): The output of the queue status command.

        Returns:
            pandas.DataFrame: The queue status as a DataFrame.
        """
        raise NotImplementedError()
