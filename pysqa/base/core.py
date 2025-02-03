import getpass
import importlib
import os
import subprocess
from typing import Optional, Union

import pandas
from jinja2 import Template

from pysqa.base.abstract import QueueAdapterAbstractClass
from pysqa.wrapper.abstract import SchedulerCommands

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


def execute_command(
    commands: str,
    working_directory: Optional[str] = None,
    split_output: bool = True,
    shell: bool = False,
    error_filename: str = "pysqa.err",
) -> Union[str, list[str]]:
    """
    A wrapper around the subprocess.check_output function.

    Args:
        commands (str): The command(s) to be executed on the command line
        working_directory (str, optional): The directory where the command is executed. Defaults to None.
        split_output (bool, optional): Boolean flag to split newlines in the output. Defaults to True.
        shell (bool, optional): Additional switch to convert commands to a single string. Defaults to False.
        error_filename (str, optional): In case the execution fails, the output is written to this file. Defaults to "pysqa.err".

    Returns:
        Union[str, List[str]]: Output of the shell command either as a string or as a list of strings
    """
    if shell and isinstance(commands, list):
        commands = " ".join(commands)
    try:
        out = subprocess.check_output(
            commands,
            cwd=working_directory,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=not isinstance(commands, list),
        )
    except subprocess.CalledProcessError as e:
        with open(os.path.join(working_directory, error_filename), "w") as f:
            print(e.stdout, file=f)
        out = None
    if out is not None and split_output:
        return out.split("\n")
    else:
        return out


def get_queue_commands(queue_type: str) -> Union[SchedulerCommands, None]:
    """
    Load queuing system commands class

    Args:
        queue_type (str): Type of the queuing system in capital letters

    Returns:
        SchedulerCommands: queuing system commands class instance
    """
    if queue_type in queue_type_dict:
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


class QueueAdapterCore(QueueAdapterAbstractClass):
    """
    The goal of the QueueAdapter class is to make submitting to a queue system as easy as starting another sub process
    locally.

    Args:
        queue_type (str): Type of the queuing system in capital letters
        execute_command (funct): Function to execute commands.
    """

    def __init__(
        self,
        queue_type: str,
        execute_command: callable = execute_command,
    ):
        self._commands = get_queue_commands(queue_type=queue_type)
        if queue_type_dict[queue_type]["module_name"] is not None:
            self._submission_template = importlib.import_module(
                queue_type_dict[queue_type]["module_name"]
            ).template
        self._execute_command_function = execute_command

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
        if submission_template is None:
            submission_template = self._submission_template
        working_directory, queue_script_path = self._write_queue_script(
            queue=queue,
            job_name=job_name,
            working_directory=working_directory,
            cores=cores,
            memory_max=memory_max,
            run_time_max=run_time_max,
            command=command,
            dependency_list=dependency_list,
            submission_template=submission_template,
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

    def get_status_of_jobs(self, process_id_lst: list[int]) -> list[str]:
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

    def _list_command_to_be_executed(self, queue_script_path: str) -> list:
        """
        Get the list of commands to be executed.

        Args:
            queue_script_path (str): The path to the queue script.

        Returns:
            list: The list of commands to be executed.
        """
        return self._commands.submit_job_command + [queue_script_path]

    def _execute_command(
        self,
        commands: Union[str, list[str]],
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

    def _write_queue_script(
        self,
        queue: Optional[str] = None,
        submission_template: Optional[Union[str, Template]] = None,
        job_name: Optional[str] = None,
        working_directory: Optional[str] = None,
        cores: Optional[int] = None,
        memory_max: Optional[int] = None,
        run_time_max: Optional[int] = None,
        dependency_list: Optional[list[int]] = None,
        command: Optional[str] = None,
        **kwargs,
    ) -> tuple[str, str]:
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
            submission_template=submission_template,
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
        if queue is not None:
            raise ValueError()
        if submission_template is None:
            submission_template = self._submission_template
        return self._commands.render_submission_template(
            command=command,
            submission_template=submission_template,
            working_directory=working_directory,
            job_name=job_name,
            cores=cores,
            memory_max=memory_max,
            run_time_max=run_time_max,
            dependency_list=dependency_list,
            **kwargs,
        )

    @staticmethod
    def _get_user() -> str:
        """
        Get the current user.

        Returns:
            str: The current user.
        """
        return getpass.getuser()
