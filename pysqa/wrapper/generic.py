# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

from abc import ABC, abstractmethod
from typing import List, Optional, Union

from jinja2 import Template
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
    def enable_reservation_command(self) -> list[str]:
        """
        Returns the command to enable job reservation on the scheduler.

        Returns:
            list[str]: The command to enable job reservation.
        """
        raise NotImplementedError()

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
    @abstractmethod
    def get_queue_status_command(self) -> list[str]:
        """
        Returns the command to get the status of the job queue.

        Returns:
            list[str]: The command to get the queue status.
        """
        pass

    @staticmethod
    @abstractmethod
    def render_submission_template(
        command: str,
        submission_template: Union[str, Template],
        working_directory: str,
        job_name: str = "pysqa",
        cores: int = 1,
        memory_max: Optional[int] = None,
        run_time_max: Optional[int] = None,
        dependency_list: Optional[List[int]] = None,
        **kwargs,
    ) -> str:
        """
        Generate the job submission template.

        Args:
            command (str, optional): The command to be executed.
            job_name (str, optional): The job name. Defaults to "pysqa".
            working_directory (str, optional): The working directory. Defaults to ".".
            cores (int, optional): The number of cores. Defaults to 1.
            memory_max (int, optional): The maximum memory. Defaults to None.
            run_time_max (int, optional): The maximum run time. Defaults to None.
            dependency_list (list[int], optional): The list of dependency job IDs. Defaults to None.
            submission_template (str): Submission script template pysqa.wrapper.torque.template

        Returns:
            str: The rendered job submission template.
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
