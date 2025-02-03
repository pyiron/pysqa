from abc import ABC, abstractmethod
from typing import Optional, Union

import pandas
from jinja2 import Template


class QueueAdapterAbstractClass(ABC):
    @abstractmethod
    def submit_job(
        self,
        queue: Optional[str] = None,
        job_name: Optional[str] = None,
        working_directory: Optional[str] = None,
        cores: Optional[int] = None,
        memory_max: Optional[int] = None,
        run_time_max: Optional[int] = None,
        dependency_list: Optional[list[str]] = None,
        command: Optional[str] = None,
        submission_template: Optional[Union[str, Template]] = None,
        **kwargs,
    ) -> Union[int, None]:
        pass

    @abstractmethod
    def enable_reservation(self, process_id: int):
        pass

    @abstractmethod
    def delete_job(self, process_id: int) -> Union[str, None]:
        pass

    @abstractmethod
    def get_queue_status(self, user: Optional[str] = None) -> pandas.DataFrame:
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
    def get_status_of_job(self, process_id: int) -> Union[str, None]:
        """
        Get the status of a job.

        Args:
            process_id (int): The process ID.

        Returns:
            str: The status of the job.results_lst.append(df_selected.values[0])
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
