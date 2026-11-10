import os
from abc import ABC, abstractmethod

import pandas
from jinja2 import Template


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

    def get_job_status_command(self, process_id: int) -> list[str] | None:
        """
        Returns the command to query the status of a single job from the accounting database of the scheduler. This is
        used as fallback for jobs which are no longer listed in the queue status, for example because they already
        finished. Queuing systems without such an accounting database return None.

        Args:
            process_id (int): The queuing system ID of the job.

        Returns:
            list[str] | None: The command to query the job status or None if not supported.
        """
        return None

    @staticmethod
    def convert_job_status(job_status_output: str) -> str | None:
        """
        Converts the output of the job status command to the pysqa job status.

        Args:
            job_status_output (str): The output of the job status command.

        Returns:
            str | None: The status of the job or None if the job is unknown.
        """
        return None

    @staticmethod
    def render_submission_template(
        command: str,
        submission_template: str | Template,
        job_name: str = "pysqa",
        working_directory: str = os.path.abspath("."),
        cores: int = 1,
        memory_max: int | str | None = None,
        run_time_max: int | None = None,
        dependency_list: list[int] | None = None,
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
        if not isinstance(submission_template, Template):
            submission_template = Template(submission_template)
        return submission_template.render(
            command=command,
            job_name=job_name,
            working_directory=working_directory,
            cores=cores,
            memory_max=memory_max,
            run_time_max=run_time_max,
            dependency_list=dependency_list,
            **kwargs,
        )

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
