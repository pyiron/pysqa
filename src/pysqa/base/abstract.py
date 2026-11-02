from abc import ABC, abstractmethod

import pandas
from jinja2 import Template


class QueueAdapterAbstractClass(ABC):
    @abstractmethod
    def submit_job(
        self,
        queue: str | None = None,
        job_name: str = "pysqa",
        working_directory: str | None = None,
        cores: int = 1,
        memory_max: int | str | None = None,
        run_time_max: int | None = None,
        dependency_list: list[int] | None = None,
        command: str = "",
        submission_template: str | Template | None = None,
        **kwargs,
    ) -> int | None:
        pass

    @abstractmethod
    def enable_reservation(self, process_id: int):
        pass

    @abstractmethod
    def delete_job(self, process_id: int) -> str | None:
        pass

    @abstractmethod
    def get_queue_status(self, user: str | None = None) -> pandas.DataFrame:
        """
        Get the status of the queue.

        Args:
            user (str): The user to filter the queue status for.

        Returns:
            pandas.DataFrame: The queue status.
        """
        pass

    @abstractmethod
    def get_status_of_my_jobs(self) -> pandas.DataFrame:
        """
        Get the status of the user's jobs.

        Returns:
            pandas.DataFrame: The status of the user's jobs.
        """
        pass

    @abstractmethod
    def get_status_of_job(self, process_id: int) -> str | None:
        """
        Get the status of a job.

        Args:
            process_id (int): The process ID.

        Returns:
            str: The status of the job.
        """
        pass

    @abstractmethod
    def get_status_of_jobs(self, process_id_lst: list[int]) -> list[str]:
        """
        Get the status of multiple jobs.

        Args:
            process_id_lst (list[int]): List of process IDs.

        Returns:
            list[str]: List of job statuses.
        """
        pass
