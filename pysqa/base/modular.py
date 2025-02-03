from typing import Optional, Union

import pandas

from pysqa.base.config import QueueAdapterWithConfig
from pysqa.base.core import execute_command


class ModularQueueAdapter(QueueAdapterWithConfig):
    """
    A class representing a modular queue adapter.

    Args:
        config (dict): The configuration dictionary.
        directory (str, optional): The directory path. Defaults to "~/.queues".
        execute_command (callable, optional): The execute command function. Defaults to execute_command.

    Attributes:
        _queue_to_cluster_dict (dict): A dictionary mapping queues to clusters.

    Raises:
        ValueError: If a cluster is not found in the list of clusters.

    """

    def __init__(
        self,
        config: dict,
        directory: str = "~/.queues",
        execute_command: callable = execute_command,
    ):
        super().__init__(
            config=config, directory=directory, execute_command=execute_command
        )
        self._queue_to_cluster_dict = {
            k: v["cluster"] for k, v in self._config["queues"].items()
        }
        for v in self._queue_to_cluster_dict.values():
            if v not in self._config["cluster"]:
                raise ValueError(
                    "The cluster "
                    + v
                    + " was not found in the list of clusters "
                    + str(list(self._config["cluster"].keys()))
                )

    def submit_job(
        self,
        queue: Optional[str] = None,
        job_name: Optional[str] = None,
        working_directory: Optional[str] = None,
        cores: Optional[int] = None,
        memory_max: Optional[str] = None,
        run_time_max: Optional[int] = None,
        dependency_list: Optional[list[str]] = None,
        command: Optional[str] = None,
        **kwargs,
    ) -> Union[int, None]:
        """
        Submit a job to the queue.

        Args:
            queue (str, optional): The queue name. Defaults to None.
            job_name (str, optional): The job name. Defaults to None.
            working_directory (str, optional): The working directory. Defaults to None.
            cores (int, optional): The number of cores. Defaults to None.
            memory_max (int, optional): The maximum memory. Defaults to None.
            run_time_max (int, optional): The maximum run time. Defaults to None.
            dependency_list (list[str], optional): The list of dependencies. Defaults to None.
            command (str, optional): The command to execute. Defaults to None.

        Returns:
            int: The cluster queue ID.

        """
        working_directory, queue_script_path = self._write_queue_script(
            queue=queue,
            job_name=job_name,
            working_directory=working_directory,
            cores=cores,
            memory_max=memory_max,
            run_time_max=run_time_max,
            dependency_list=dependency_list,
            command=command,
            **kwargs,
        )
        cluster_module = self._queue_to_cluster_dict[queue]
        commands = self._switch_cluster_command(
            cluster_module=cluster_module
        ) + self._list_command_to_be_executed(queue_script_path=queue_script_path)
        out = self._execute_command(
            commands=commands,
            working_directory=working_directory,
            split_output=False,
            shell=True,
        )
        if out is not None:
            cluster_queue_id = self._commands.get_job_id_from_output(out)
            cluster_queue_id *= 10
            cluster_queue_id += self._config["cluster"].index(cluster_module)
            return cluster_queue_id
        else:
            return None

    def enable_reservation(self, process_id: int):
        """
        Enable reservation for a process.

        Args:
            process_id (int): The process ID.

        Returns:
            str: The output of the enable reservation command.

        """
        cluster_module, cluster_queue_id = self._resolve_queue_id(
            process_id=process_id, cluster_dict=self._config["cluster"]
        )
        cluster_commands = self._switch_cluster_command(cluster_module=cluster_module)
        commands = (
            cluster_commands
            + self._commands.enable_reservation_command
            + [str(cluster_queue_id)]
        )
        out = self._execute_command(commands=commands, split_output=True, shell=True)
        if out is not None:
            return out[0]
        else:
            return None

    def delete_job(self, process_id: int):
        """
        Delete a job.

        Args:
            process_id (int): The process ID.

        Returns:
            str: The output of the delete job command.

        """
        cluster_module, cluster_queue_id = self._resolve_queue_id(
            process_id=process_id, cluster_dict=self._config["cluster"]
        )
        cluster_commands = self._switch_cluster_command(cluster_module=cluster_module)
        commands = (
            cluster_commands
            + self._commands.delete_job_command
            + [str(cluster_queue_id)]
        )
        out = self._execute_command(commands=commands, split_output=True, shell=True)
        if out is not None:
            return out[0]
        else:
            return None

    def get_queue_status(self, user: Optional[str] = None) -> pandas.DataFrame:
        """
        Get the queue status.

        Args:
            user (str, optional): The user name. Defaults to None.

        Returns:
            pandas.DataFrame: The queue status.

        """
        df_lst = []
        for cluster_module in self._config["cluster"]:
            cluster_commands = self._switch_cluster_command(
                cluster_module=cluster_module
            )
            out = self._execute_command(
                commands=cluster_commands + self._commands.get_queue_status_command,
                split_output=False,
                shell=True,
            )
            df = self._commands.convert_queue_status(queue_status_output=out)
            df_lst.append(df)
        df = pandas.concat(df_lst, axis=0, sort=False).reset_index(drop=True)
        if user is None:
            return df
        else:
            return df[df["user"] == user]

    @staticmethod
    def _resolve_queue_id(process_id: int, cluster_dict: dict):
        """
        Resolve the queue ID.

        Args:
            process_id (int): The process ID.
            cluster_dict (dict): The cluster dictionary.

        Returns:
            tuple: The cluster module and cluster queue ID.

        """
        cluster_queue_id = int(process_id / 10)
        cluster_module = cluster_dict[process_id - cluster_queue_id * 10]
        return cluster_module, cluster_queue_id

    @staticmethod
    def _switch_cluster_command(cluster_module: str):
        """
        Generate the switch cluster command.

        Args:
            cluster_module (str): The cluster module.

        Returns:
            list: The switch cluster command.

        """
        return ["module", "--quiet", "swap", f"cluster/{cluster_module};"]
