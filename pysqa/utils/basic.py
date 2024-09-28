# coding: utf-8
# Copyright (c) Jan Janssen

import getpass
import importlib
import os
import re
from typing import List, Optional, Tuple, Union

import pandas
from jinja2 import Template
from jinja2.exceptions import TemplateSyntaxError

from pysqa.utils.execute import execute_command
from pysqa.utils.queues import Queues
from pysqa.wrapper.generic import SchedulerCommands

queue_type_dict = {
    "SGE": {
        "class_name": "SunGridEngineCommands",
        "module_name": "pysqa.wrapper.sge",
    },
    "TORQUE": {
        "class_name": "TorqueCommands",
        "module_name": "pysqa.wrapper.torque",
    },
    "SLURM": {
        "class_name": "SlurmCommands",
        "module_name": "pysqa.wrapper.slurm",
    },
    "LSF": {
        "class_name": "LsfCommands",
        "module_name": "pysqa.wrapper.lsf",
    },
    "MOAB": {
        "class_name": "MoabCommands",
        "module_name": "pysqa.wrapper.moab",
    },
    "GENT": {
        "class_name": "GentCommands",
        "module_name": "pysqa.wrapper.gent",
    },
    "REMOTE": {
        "class_name": None,
        "module_name": None,
    },
    "FLUX": {
        "class_name": "FluxCommands",
        "module_name": "pysqa.wrapper.flux",
    },
}


def get_queue_commands(queue_type: str) -> Union[SchedulerCommands, None]:
    """
    Load queuing system commands class

    Args:
        queue_type (str): Type of the queuing system in capital letters

    Returns:
        SchedulerCommands: queuing system commands class instance
    """
    if queue_type in queue_type_dict.keys():
        class_name = queue_type_dict[queue_type]["class_name"]
        module_name = queue_type_dict[queue_type]["module_name"]
        if module_name is not None and class_name is not None:
            return getattr(importlib.import_module(module_name), class_name)()
        else:
            return None
    else:
        raise ValueError(
            "The queue_type "
            + queue_type
            + " is not found in the list of supported queue types "
            + str(list(queue_type_dict.keys()))
        )


class BasisQueueAdapter(object):
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
        self._config = config
        self._fill_queue_dict(queue_lst_dict=self._config["queues"])
        self._load_templates(queue_lst_dict=self._config["queues"], directory=directory)
        self._commands = get_queue_commands(queue_type=self._config["queue_type"])
        self._queues = Queues(self.queue_list)
        self._remote_flag = False
        self._ssh_delete_file_on_remote = True
        self._execute_command_function = execute_command

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

    def submit_job(
        self,
        queue: Optional[str] = None,
        job_name: Optional[str] = None,
        working_directory: Optional[str] = None,
        cores: Optional[int] = None,
        memory_max: Optional[int] = None,
        run_time_max: Optional[int] = None,
        dependency_list: Optional[List[str]] = None,
        command: Optional[str] = None,
        **kwargs,
    ) -> Union[int, None]:
        """
        Submit a job to the queue.

        Args:
            queue (str/None): The queue to submit the job to.
            job_name (str/None): The name of the job.
            working_directory (str/None): The working directory for the job.
            cores (int/None): The number of cores required for the job.
            memory_max (int/None): The maximum memory required for the job.
            run_time_max (int/None): The maximum run time for the job.
            dependency_list (list[str]/None): List of job dependencies.
            command (str/None): The command to execute for the job.

        Returns:
            int: The job ID.
        """
        if working_directory is not None and " " in working_directory:
            raise ValueError(
                "Whitespaces in the working_directory name are not supported!"
            )
        working_directory, queue_script_path = self._write_queue_script(
            queue=queue,
            job_name=job_name,
            working_directory=working_directory,
            cores=cores,
            memory_max=memory_max,
            run_time_max=run_time_max,
            command=command,
            **kwargs,
        )
        out = self._execute_command(
            commands=self._list_command_to_be_executed(
                queue_script_path=queue_script_path
            ),
            working_directory=working_directory,
            split_output=False,
        )
        if out is not None:
            return self._commands.get_job_id_from_output(out)
        else:
            return None

    def _list_command_to_be_executed(self, queue_script_path: str) -> list:
        """
        Get the list of commands to be executed.

        Args:
            queue_script_path (str): The path to the queue script.

        Returns:
            list: The list of commands to be executed.
        """
        return self._commands.submit_job_command + [queue_script_path]

    def enable_reservation(self, process_id: int):
        """
        Enable reservation for a process.

        Args:
            process_id (int): The process ID.

        Returns:
            str: The result of the enable reservation command.
        """
        out = self._execute_command(
            commands=self._commands.enable_reservation_command + [str(process_id)],
            split_output=True,
        )
        if out is not None:
            return out[0]
        else:
            return None

    def delete_job(self, process_id: int) -> Union[str, None]:
        """
        Delete a job.

        Args:
            process_id (int): The process ID.

        Returns:
            str: The result of the delete job command.
        """
        out = self._execute_command(
            commands=self._commands.delete_job_command + [str(process_id)],
            split_output=True,
        )
        if out is not None:
            return out[0]
        else:
            return None

    def get_queue_status(self, user: Optional[str] = None) -> pandas.DataFrame:
        """
        Get the status of the queue.

        Args:
            user (str): The user to filter the queue status for.

        Returns:
            pandas.DataFrame: The queue status.
        """
        out = self._execute_command(
            commands=self._commands.get_queue_status_command, split_output=False
        )
        df = self._commands.convert_queue_status(queue_status_output=out)
        if user is None:
            return df
        else:
            return df[df["user"] == user]

    def get_status_of_my_jobs(self) -> pandas.DataFrame:
        """
        Get the status of the user's jobs.

        Returns:
            pandas.DataFrame: The status of the user's jobs.
        """
        return self.get_queue_status(user=self._get_user())

    def get_status_of_job(self, process_id: int) -> Union[str, None]:
        """
        Get the status of a job.

        Args:
            process_id (int): The process ID.

        Returns:
            str: The status of the job.results_lst.append(df_selected.values[0])
        """
        df = self.get_queue_status()
        df_selected = df[df["jobid"] == process_id]["status"]
        if len(df_selected) != 0:
            return df_selected.values[0]
        else:
            return None

    def get_status_of_jobs(self, process_id_lst: List[int]) -> List[str]:
        """
        Get the status of multiple jobs.

        Args:
            process_id_lst (list[int]): List of process IDs.

        Returns:
            list[str]: List of job statuses.
        """
        df = self.get_queue_status()
        results_lst = []
        for process_id in process_id_lst:
            df_selected = df[df["jobid"] == process_id]["status"]
            if len(df_selected) != 0:
                results_lst.append(df_selected.values[0])
            else:
                results_lst.append("finished")
        return results_lst

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
        cores = self._value_in_range(
            value=cores,
            value_min=active_queue["cores_min"],
            value_max=active_queue["cores_max"],
        )
        run_time_max = self._value_in_range(
            value=run_time_max, value_max=active_queue["run_time_max"]
        )
        memory_max = self._value_in_range(
            value=memory_max, value_max=active_queue["memory_max"]
        )
        return cores, run_time_max, memory_max

    def _write_queue_script(
        self,
        queue: Optional[str] = None,
        job_name: Optional[str] = None,
        working_directory: Optional[str] = None,
        cores: Optional[int] = None,
        memory_max: Optional[int] = None,
        run_time_max: Optional[int] = None,
        dependency_list: Optional[List[int]] = None,
        command: Optional[str] = None,
        **kwargs,
    ) -> Tuple[str, str]:
        """
        Write the queue script to a file.

        Args:
            queue (str/None): The queue name.
            job_name (str/None): The job name.
            working_directory (str/None): The working directory.
            cores (int/None): The number of cores.
            memory_max (int/None): The maximum memory.
            run_time_max (int/None): The maximum run time.
            dependency_list (list/None): The list of dependency job IDs.
            command (str/None): The command to be executed.

        Returns:
            Tuple[str, str]: A tuple containing the working directory and the path to the queue script file.
        """
        if isinstance(command, list):
            command = "".join(command)
        if working_directory is None:
            working_directory = "."
        queue_script = self._job_submission_template(
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
        if not os.path.exists(working_directory):
            os.makedirs(working_directory)
        queue_script_path = os.path.join(working_directory, "run_queue.sh")
        with open(queue_script_path, "w") as f:
            f.writelines(queue_script)
        return working_directory, queue_script_path

    def _job_submission_template(
        self,
        queue: Optional[str] = None,
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
        self._value_error_if_none(value=command)
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
        template = active_queue["template"]
        return template.render(
            job_name=job_name,
            working_directory=working_directory,
            cores=cores,
            memory_max=memory_max,
            run_time_max=run_time_max,
            command=command,
            dependency_list=dependency_list,
            **kwargs,
        )

    def _execute_command(
        self,
        commands: Union[str, List[str]],
        working_directory: Optional[str] = None,
        split_output: bool = True,
        shell: bool = False,
        error_filename: str = "pysqa.err",
    ) -> str:
        """
        Execute a command or a list of commands.

        Args:
            commands (Union[str, List[str]]): The command(s) to be executed.
            working_directory (Optional[str], optional): The working directory. Defaults to None.
            split_output (bool, optional): Whether to split the output into lines. Defaults to True.
            shell (bool, optional): Whether to use the shell to execute the command. Defaults to False.
            error_filename (str, optional): The name of the error file. Defaults to "pysqa.err".

        Returns:
            str: The output of the command(s).
        """
        return self._execute_command_function(
            commands=commands,
            working_directory=working_directory,
            split_output=split_output,
            shell=shell,
            error_filename=error_filename,
        )

    @staticmethod
    def _get_user() -> str:
        """
        Get the current user.

        Returns:
            str: The current user.
        """
        return getpass.getuser()

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

    @staticmethod
    def _value_error_if_none(value: str) -> None:
        """
        Raise a ValueError if the value is None or not a string.

        Args:
            value (str/None): The value to check.

        Raises:
            ValueError: If the value is None.
            TypeError: If the value is not a string.
        """
        if value is None:
            raise ValueError("Value cannot be None.")
        if not isinstance(value, str):
            raise TypeError()

    @classmethod
    def _value_in_range(
        cls,
        value: Union[int, float, None],
        value_min: Union[int, float, None] = None,
        value_max: Union[int, float, None] = None,
    ) -> Union[int, float, None]:
        """
        Check if a value is within a specified range.

        Args:
            value (int/float/None): The value to check.
            value_min (int/float/None): The minimum value. Defaults to None.
            value_max (int/float/None): The maximum value. Defaults to None.

        Returns:
            int/float/None: The value if it is within the range, otherwise the minimum or maximum value.
        """

        if value is not None:
            value_, value_min_, value_max_ = [
                (
                    cls._memory_spec_string_to_value(v)
                    if v is not None and isinstance(v, str)
                    else v
                )
                for v in (value, value_min, value_max)
            ]
            # ATTENTION: '60000' is interpreted as '60000M' since default magnitude is 'M'
            # ATTENTION: int('60000') is interpreted as '60000B' since _memory_spec_string_to_value return the size in
            # ATTENTION: bytes, as target_magnitude = 'b'
            # We want to compare the the actual (k,m,g)byte value if there is any
            if value_min_ is not None and value_ < value_min_:
                return value_min
            if value_max_ is not None and value_ > value_max_:
                return value_max
            return value
        else:
            if value_min is not None:
                return value_min
            if value_max is not None:
                return value_max
            return value

    @staticmethod
    def _is_memory_string(value: str) -> bool:
        """
        Check if a string specifies a certain amount of memory.

        Args:
            value (str): The string to check.

        Returns:
            bool: True if the string matches a memory specification, False otherwise.
        """
        memory_spec_pattern = r"[0-9]+[bBkKmMgGtT]?"
        return re.findall(memory_spec_pattern, value)[0] == value

    @classmethod
    def _memory_spec_string_to_value(
        cls, value: str, default_magnitude: str = "m", target_magnitude: str = "b"
    ) -> Union[int, float]:
        """
        Converts a valid memory string (tested by _is_memory_string) into an integer/float value of desired
        magnitude `default_magnitude`. If it is a plain integer string (e.g.: '50000') it will be interpreted with
        the magnitude passed in by the `default_magnitude`. The output will rescaled to `target_magnitude`

        Args:
            value (str): The string to convert.
            default_magnitude (str): The magnitude for interpreting plain integer strings [b, B, k, K, m, M, g, G, t, T]. Defaults to "m".
            target_magnitude (str): The magnitude to which the output value should be converted [b, B, k, K, m, M, g, G, t, T]. Defaults to "b".

        Returns:
            Union[int, float]: The value of the string in `target_magnitude` units.
        """
        magnitude_mapping = {"b": 0, "k": 1, "m": 2, "g": 3, "t": 4}
        if cls._is_memory_string(value):
            integer_pattern = r"[0-9]+"
            magnitude_pattern = r"[bBkKmMgGtT]+"
            integer_value = int(re.findall(integer_pattern, value)[0])

            magnitude = re.findall(magnitude_pattern, value)
            if len(magnitude) > 0:
                magnitude = magnitude[0].lower()
            else:
                magnitude = default_magnitude.lower()
            # Convert it to default magnitude = megabytes
            return (integer_value * 1024 ** magnitude_mapping[magnitude]) / (
                1024 ** magnitude_mapping[target_magnitude]
            )
        else:
            return value
