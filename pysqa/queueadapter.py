import os
from typing import Optional, Union

import pandas
from jinja2 import Template

from pysqa.base.abstract import QueueAdapterAbstractClass
from pysqa.base.config import QueueAdapterWithConfig, Queues, read_config
from pysqa.base.core import QueueAdapterCore, execute_command
from pysqa.base.modular import ModularQueueAdapter


class QueueAdapter(QueueAdapterAbstractClass):
    """
    The goal of the QueueAdapter class is to make submitting to a queue system as easy as starting another sub process
    locally.

    Args:
        directory (str): directory containing the queue.yaml files as well as corresponding jinja2 templates for the
                         individual queues.

    Attributes:

        .. attribute:: config

            QueueAdapter configuration read from the queue.yaml file.

        .. attribute:: queue_list

            List of available queues

        .. attribute:: queue_view

            Pandas DataFrame representation of the available queues, read from queue.yaml.

        .. attribute:: queues

            Queues available for auto completion QueueAdapter().queues.<queue name> returns the queue name.
    """

    def __init__(
        self,
        directory: Optional[str] = None,
        queue_type: Optional[str] = None,
        execute_command: callable = execute_command,
    ):
        """
        Initialize the QueueAdapter.

        Args:
            directory (str): Directory containing the queue.yaml files and corresponding templates.
            execute_command (callable): Function to execute commands.
        """
        if directory is not None:
            queue_yaml = os.path.join(directory, "queue.yaml")
            clusters_yaml = os.path.join(directory, "clusters.yaml")
            self._adapter = None
            if os.path.exists(queue_yaml):
                self._queue_dict = {
                    "default": set_queue_adapter(
                        config=read_config(file_name=queue_yaml),
                        directory=directory,
                        execute_command=execute_command,
                    )
                }
                primary_queue = "default"
            elif os.path.exists(clusters_yaml):
                config = read_config(file_name=clusters_yaml)
                self._queue_dict = {
                    k: set_queue_adapter(
                        config=read_config(file_name=os.path.join(directory, v)),
                        directory=directory,
                        execute_command=execute_command,
                    )
                    for k, v in config["cluster"].items()
                }
                primary_queue = config["cluster_primary"]
            else:
                raise ValueError(
                    "Neither a queue.yaml file nor a clusters.yaml file were found in "
                    + directory
                )
            self._adapter = self._queue_dict[primary_queue]
        elif queue_type is not None:
            self._queue_dict = {}
            self._adapter = QueueAdapterCore(
                queue_type=queue_type.upper(),
                execute_command=execute_command,
            )
        else:
            raise ValueError()

    def list_clusters(self) -> list[str]:
        """
        List available computing clusters for remote submission

        Returns:
            List of computing clusters
        """
        return list(self._queue_dict.keys())

    def switch_cluster(self, cluster_name: str):
        """
        Switch to a different computing cluster

        Args:
            cluster_name (str): name of the computing cluster
        """
        self._adapter = self._queue_dict[cluster_name]

    @property
    def config(self) -> Union[dict, None]:
        """
        Get the QueueAdapter configuration.

        Returns:
            dict: The QueueAdapter configuration.
        """
        if isinstance(self._adapter, QueueAdapterWithConfig):
            return self._adapter.config
        else:
            return None

    @property
    def ssh_delete_file_on_remote(self) -> bool:
        """
        Get the value of ssh_delete_file_on_remote property.

        Returns:
            bool: The value of ssh_delete_file_on_remote property.
        """
        if isinstance(self._adapter, QueueAdapterWithConfig):
            return self._adapter.ssh_delete_file_on_remote
        else:
            return False

    @property
    def remote_flag(self) -> bool:
        """
        Get the value of remote_flag property.

        Returns:
            bool: The value of remote_flag property.
        """
        if isinstance(self._adapter, QueueAdapterWithConfig):
            return self._adapter.remote_flag
        else:
            return False

    @property
    def queue_list(self) -> Union[list[str], None]:
        """
        Get the list of available queues.

        Returns:
            List[str]: The list of available queues.
        """
        if isinstance(self._adapter, QueueAdapterWithConfig):
            return self._adapter.queue_list
        else:
            return None

    @property
    def queue_view(self) -> Union[pandas.DataFrame, None]:
        """
        Get the Pandas DataFrame representation of the available queues.

        Returns:
            pandas.DataFrame: The Pandas DataFrame representation of the available queues.
        """
        if isinstance(self._adapter, QueueAdapterWithConfig):
            return self._adapter.queue_view
        else:
            return None

    @property
    def queues(self) -> Union[Queues, None]:
        """
        Get the list of available queues.

        Returns:
            List[str]: The list of available queues.
        """
        if isinstance(self._adapter, QueueAdapterWithConfig):
            return self._adapter.queues
        else:
            return None

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
    ) -> int:
        """
        Submits command to the given queue.

        Args:
            queue (str/None):  Name of the queue to submit to, must be one of the names configured for this adapter
                               (optional)
            job_name (str/None):  Name of the job for the underlying queuing system (optional)
            working_directory (str/None):  Directory to run the job in (optional)
            cores (int/None):  Number of hardware threads requested (optional)
            memory_max (int/None):  Amount of memory requested per node in GB (optional)
            run_time_max (int/None):  Maximum runtime in seconds (optional)
            dependency_list(list[str]/None: Job ids of jobs to be completed before starting (optional)
            command (str/None): shell command to run in the job
            **kwargs: allows writing additional parameters to the job submission script if they are available in the
                      corresponding template.

        Returns:
            int: Job id received from the queuing system for the job which was submitted
        """
        return self._adapter.submit_job(
            queue=queue,
            job_name=job_name,
            working_directory=working_directory,
            cores=cores,
            memory_max=memory_max,
            run_time_max=run_time_max,
            dependency_list=dependency_list,
            command=command,
            submission_template=submission_template,
            **kwargs,
        )

    def enable_reservation(self, process_id: int) -> str:
        """
        Enable reservation for a process.

        Args:
            process_id (int): The process id.

        Returns:
            str: The result of enabling reservation.
        """
        return self._adapter.enable_reservation(process_id=process_id)

    def get_job_from_remote(self, working_directory: str):
        """
        Get the results of the calculation - this is necessary when the calculation was executed on a remote host.

        Args:
            working_directory (str): The working directory.
        """
        if isinstance(self._adapter, QueueAdapterWithConfig):
            self._adapter.get_job_from_remote(working_directory=working_directory)
        else:
            raise TypeError()

    def transfer_file_to_remote(
        self,
        file: str,
        transfer_back: bool = False,
        delete_file_on_remote: bool = False,
    ):
        """
        Transfer file from remote host to local host.

        Args:
            file (str): The file to transfer.
            transfer_back (bool): Whether to transfer the file back.
            delete_file_on_remote (bool): Whether to delete the file on the remote host.
        """
        if isinstance(self._adapter, QueueAdapterWithConfig):
            self._adapter.transfer_file(
                file=file,
                transfer_back=transfer_back,
                delete_file_on_remote=delete_file_on_remote,
            )
        else:
            raise TypeError()

    def convert_path_to_remote(self, path: str) -> str:
        """
        Convert a local path to a remote path.

        Args:
            path (str): The local path.

        Returns:
            str: The remote path.
        """
        if isinstance(self._adapter, QueueAdapterWithConfig):
            return self._adapter.convert_path_to_remote(path=path)
        else:
            raise TypeError()

    def delete_job(self, process_id: int) -> str:
        """
        Delete a job.

        Args:
            process_id (int): The process id.

        Returns:
            str: The result of deleting the job.
        """
        return self._adapter.delete_job(process_id=process_id)

    def get_queue_status(self, user: Optional[str] = None) -> pandas.DataFrame:
        """
        Get the status of the queue.

        Args:
            user (str/None): The user.

        Returns:
            pandas.DataFrame: The status of the queue.
        """
        return self._adapter.get_queue_status(user=user)

    def get_status_of_my_jobs(self) -> pandas.DataFrame:
        """
        Get the status of the user's jobs.

        Returns:
           pandas.DataFrame: The status of the user's jobs.
        """
        return self._adapter.get_status_of_my_jobs()

    def get_status_of_job(self, process_id: int) -> str:
        """
        Get the status of a job.

        Args:
            process_id: The process id.

        Returns:
             str: The status of the job. Possible values are ['running', 'pending', 'error'].
        """
        return self._adapter.get_status_of_job(process_id=process_id)

    def get_status_of_jobs(self, process_id_lst: list[int]) -> list[str]:
        """
        Get the status of multiple jobs.

        Args:
            process_id_lst: The list of process ids.

        Returns:
             List[str]: The status of the jobs. Possible values are ['running', 'pending', 'error', ...].
        """
        return self._adapter.get_status_of_jobs(process_id_lst=process_id_lst)

    def check_queue_parameters(
        self,
        queue: str,
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
            queue (str/None): The queue name.
            cores (int): The number of cores.
            run_time_max (int/None): The maximum runtime.
            memory_max (int/None): The maximum memory.
            active_queue (dict/None): The active queue.

        Returns:
            List: A list containing the checked parameters [cores, run_time_max, memory_max].
        """
        if isinstance(self._adapter, QueueAdapterWithConfig):
            return self._adapter.check_queue_parameters(
                queue=queue,
                cores=cores,
                run_time_max=run_time_max,
                memory_max=memory_max,
                active_queue=active_queue,
            )
        else:
            return cores, run_time_max, memory_max


def set_queue_adapter(
    config: dict, directory: str, execute_command: callable = execute_command
):
    """
    Initialize the queue adapter

    Args:
        config (dict): configuration for one cluster
        directory (str): directory which contains the queue configurations
    """
    if config["queue_type"] in ["SGE", "TORQUE", "SLURM", "LSF", "MOAB", "FLUX"]:
        return QueueAdapterWithConfig(
            config=config, directory=directory, execute_command=execute_command
        )
    elif config["queue_type"] in ["GENT"]:
        return ModularQueueAdapter(
            config=config, directory=directory, execute_command=execute_command
        )
    elif config["queue_type"] in ["REMOTE"]:
        # The RemoteQueueAdapter has additional dependencies, namely paramiko and tqdm.
        # By moving the import to this line it only fails when the user specifies the
        # RemoteQueueAdapter in their pysqa configuration.
        from pysqa.base.remote import RemoteQueueAdapter

        return RemoteQueueAdapter(
            config=config, directory=directory, execute_command=execute_command
        )
    else:
        raise ValueError(
            "The queue_type "
            + config["queue_type"]
            + " is not found in the list of supported queue types "
            + str(["SGE", "TORQUE", "SLURM", "LSF", "MOAB", "FLUX", "GENT", "REMOTE"])
        )
