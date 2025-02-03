import os
from typing import Optional, Union

import pandas
import yaml
from jinja2 import Template
from jinja2.exceptions import TemplateSyntaxError

from pysqa.base.core import QueueAdapterCore, execute_command
from pysqa.base.validate import check_queue_parameters, value_error_if_none


class Queues:
    """
    Queues is an abstract class simply to make the list of queues available for auto completion. This is mainly used in
    interactive environments like jupyter.
    """

    def __init__(self, list_of_queues: list[str]):
        """
        Initialize the Queues object.

        Args:
            list_of_queues (List[str]): A list of queue names.

        """
        self._list_of_queues = list_of_queues

    def __getattr__(self, item: str) -> str:
        """
        Get the queue name.

        Args:
            item (str): The name of the queue.

        Returns:
            str: The name of the queue.

        Raises:
            AttributeError: If the queue name is not in the list of queues.

        """
        if item in self._list_of_queues:
            return item
        else:
            raise AttributeError

    def __dir__(self) -> list[str]:
        """
        Get the list of queues.

        Returns:
            List[str]: The list of queues.

        """
        return self._list_of_queues


class QueueAdapterWithConfig(QueueAdapterCore):
    """
    The goal of the QueueAdapter class is to make submitting to a queue system as easy as starting another sub process
    locally.

    Args:
        config (dict): Configuration for the QueueAdapter.
        directory (str): Directory containing the queue.yaml files as well as corresponding jinja2 templates for the individual queues.
        execute_command(funct): Function to execute commands.
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
    ) -> tuple[
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
        return check_queue_parameters(
            active_queue=active_queue,
            cores=cores,
            run_time_max=run_time_max,
            memory_max=memory_max,
        )

    def _job_submission_template(
        self,
        queue: Optional[str] = None,
        submission_template: Optional[Union[str, Template]] = None,
        job_name: str = "job.py",
        working_directory: str = ".",
        cores: Optional[int] = None,
        memory_max: Optional[int] = None,
        run_time_max: Optional[int] = None,
        dependency_list: Optional[list[int]] = None,
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
            if "script" in queue_dict:
                with open(os.path.join(directory, queue_dict["script"])) as f:
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


def read_config(file_name: str = "queue.yaml") -> dict:
    """
    Read and parse a YAML configuration file.

    Args:
        file_name (str): The name of the YAML file to read.

    Returns:
        dict: The parsed configuration as a dictionary.
    """
    with open(file_name) as f:
        return yaml.load(f, Loader=yaml.FullLoader)
