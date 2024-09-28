import os
from typing import List, Optional, Tuple, Union

import pandas
from jinja2 import Template
from jinja2.exceptions import TemplateSyntaxError

from pysqa.utils.core import CoreQueueAdapter
from pysqa.utils.execute import execute_command
from pysqa.utils.queues import Queues
from pysqa.utils.validate import value_error_if_none, value_in_range


class BasisQueueAdapter(CoreQueueAdapter):
    """
    The goal of the QueueAdapter class is to make submitting to a queue system as easy as starting another sub process
    locally.

    Args:
        config (dict): Configuration for the QueueAdapter.
        directory (str): Directory containing the queue.yaml files as well as corresponding jinja2 templates for the individual queues.
        execute_command(funct): Function to execute commands.

    Attributes:
        config (dict): QueueAdapter configuration read from the queue.yaml file.
        queue_list (list): List of available queues.
        queue_view (pandas.DataFrame): Pandas DataFrame representation of the available queues, read from queue.yaml.
        queues: Queues available for auto completion QueueAdapter().queues.<queue name> returns the queue name.
    """

    def __init__(
        self,
        config: dict,
        directory: str = "~/.queues",
        execute_command: callable = execute_command,
    ):
        super().__init__(
            queue_type=config["queue_type"], execute_command=execute_command
        )
        self._config = config
        self._fill_queue_dict(queue_lst_dict=self._config["queues"])
        self._load_templates(queue_lst_dict=self._config["queues"], directory=directory)
        self._queues = Queues(self.queue_list)
        self._remote_flag = False
        self._ssh_delete_file_on_remote = True

    @property
    def ssh_delete_file_on_remote(self) -> bool:
        """
        Get the value of ssh_delete_file_on_remote.

        Returns:
            bool: The value of ssh_delete_file_on_remote.
        """
        return self._ssh_delete_file_on_remote

    @property
    def remote_flag(self) -> bool:
        """
        Get the value of remote_flag.

        Returns:
            bool: The value of remote_flag.
        """
        return self._remote_flag

    @property
    def config(self) -> dict:
        """
        Get the QueueAdapter configuration.

        Returns:
            dict: The QueueAdapter configuration.
        """
        return self._config

    @property
    def queue_list(self) -> list:
        """
        Get the list of available queues.

        Returns:
            list: The list of available queues.
        """
        return list(self._config["queues"].keys())

    @property
    def queue_view(self) -> pandas.DataFrame:
        """
        Get the Pandas DataFrame representation of the available queues.

        Returns:
            pandas.DataFrame: The Pandas DataFrame representation of the available queues.
        """
        return pandas.DataFrame(self._config["queues"]).T.drop(
            ["script", "template"], axis=1
        )

    @property
    def queues(self):
        """
        Get the available queues.

        Returns:
            Queues: The available queues.
        """
        return self._queues

    def get_job_from_remote(self, working_directory: str) -> None:
        """
        Get the results of the calculation - this is necessary when the calculation was executed on a remote host.

        Args:
            working_directory (str): The working directory where the calculation was executed.
        """
        raise NotImplementedError

    def convert_path_to_remote(self, path: str):
        """
        Converts a local file path to a remote file path.

        Args:
            path (str): The local file path to be converted.

        Returns:
            str: The converted remote file path.
        """
        raise NotImplementedError

    def transfer_file(
        self,
        file: str,
        transfer_back: bool = False,
        delete_file_on_remote: bool = False,
    ):
        """
        Transfer a file to a remote location.

        Args:
            file (str): The path of the file to be transferred.
            transfer_back (bool, optional): Whether to transfer the file back after processing. Defaults to False.
            delete_file_on_remote (bool, optional): Whether to delete the file on the remote location after transfer. Defaults to False.
        """
        raise NotImplementedError

    def check_queue_parameters(
        self,
        queue: Optional[str],
        cores: int = 1,
        run_time_max: Optional[int] = None,
        memory_max: Optional[int] = None,
        active_queue: Optional[dict] = None,
    ) -> Tuple[
        Union[float, int, None], Union[float, int, None], Union[float, int, None]
    ]:
        """
        Check the parameters of a queue.

        Args:
            queue (str): The queue to check.
            cores (int, optional): The number of cores. Defaults to 1.
            run_time_max (int, optional): The maximum run time. Defaults to None.
            memory_max (int, optional): The maximum memory. Defaults to None.
            active_queue (dict, optional): The active queue. Defaults to None.

        Returns:
            list: A list of queue parameters [cores, run_time_max, memory_max].
        """
        if active_queue is None:
            active_queue = self._config["queues"][queue]
        cores = value_in_range(
            value=cores,
            value_min=active_queue["cores_min"],
            value_max=active_queue["cores_max"],
        )
        run_time_max = value_in_range(
            value=run_time_max, value_max=active_queue["run_time_max"]
        )
        memory_max = value_in_range(
            value=memory_max, value_max=active_queue["memory_max"]
        )
        return cores, run_time_max, memory_max

    def _job_submission_template(
        self,
        queue: Optional[str] = None,
        submission_template: Optional[Union[str, Template]] = None,
        job_name: str = "job.py",
        working_directory: str = ".",
        cores: Optional[int] = None,
        memory_max: Optional[int] = None,
        run_time_max: Optional[int] = None,
        dependency_list: Optional[List[int]] = None,
        command: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate the job submission template.

        Args:
            queue (str, optional): The queue name. Defaults to None.
            job_name (str, optional): The job name. Defaults to "job.py".
            working_directory (str, optional): The working directory. Defaults to ".".
            cores (int, optional): The number of cores. Defaults to None.
            memory_max (int, optional): The maximum memory. Defaults to None.
            run_time_max (int, optional): The maximum run time. Defaults to None.
            dependency_list (list[int], optional): The list of dependency job IDs. Defaults to None.
            command (str, optional): The command to be executed. Defaults to None.

        Returns:
            str: The job submission template.
        """
        if queue is None:
            queue = self._config["queue_primary"]
        value_error_if_none(value=command)
        if queue not in self.queue_list:
            raise ValueError(
                "The queue "
                + queue
                + " was not found in the list of queues: "
                + str(self.queue_list)
            )
        active_queue = self._config["queues"][queue]
        cores, run_time_max, memory_max = self.check_queue_parameters(
            queue=None,
            cores=cores,
            run_time_max=run_time_max,
            memory_max=memory_max,
            active_queue=active_queue,
        )
        return super()._job_submission_template(
            queue=None,
            submission_template=active_queue["template"],
            job_name=job_name,
            working_directory=working_directory,
            cores=cores,
            memory_max=memory_max,
            run_time_max=run_time_max,
            dependency_list=dependency_list,
            command=command,
            **kwargs,
        )

    @staticmethod
    def _fill_queue_dict(queue_lst_dict: dict):
        """
        Fill missing keys in the queue dictionary with None values.

        Args:
            queue_lst_dict (dict): The queue dictionary.
        """
        queue_keys = ["cores_min", "cores_max", "run_time_max", "memory_max"]
        for queue_dict in queue_lst_dict.values():
            for key in set(queue_keys) - set(queue_dict.keys()):
                queue_dict[key] = None

    @staticmethod
    def _load_templates(queue_lst_dict: dict, directory: str = ".") -> None:
        """
        Load the queue templates from files and store them in the queue dictionary.

        Args:
            queue_lst_dict (dict): The queue dictionary.
            directory (str, optional): The directory where the queue template files are located. Defaults to ".".
        """
        for queue_dict in queue_lst_dict.values():
            if "script" in queue_dict.keys():
                with open(os.path.join(directory, queue_dict["script"]), "r") as f:
                    try:
                        queue_dict["template"] = Template(f.read())
                    except TemplateSyntaxError as error:
                        raise TemplateSyntaxError(
                            message="File: "
                            + queue_dict["script"]
                            + " - "
                            + error.message,
                            lineno=error.lineno,
                        )
