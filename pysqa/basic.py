# coding: utf-8
# Copyright (c) Jan Janssen

import getpass
import importlib
from jinja2 import Template
import os
import subprocess
import re
import pandas
from pysqa.queues import Queues


class BasisQueueAdapter(object):
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

    def __init__(self, config, directory="~/.queues"):
        self._config = config
        self._fill_queue_dict(queue_lst_dict=self._config["queues"])
        self._load_templates(queue_lst_dict=self._config["queues"], directory=directory)
        if self._config["queue_type"] == "SGE":
            class_name = "SunGridEngineCommands"
            module_name = "pysqa.wrapper.sge"
        elif self._config["queue_type"] == "TORQUE":
            class_name = "TorqueCommands"
            module_name = "pysqa.wrapper.torque"
        elif self._config["queue_type"] == "SLURM":
            class_name = "SlurmCommands"
            module_name = "pysqa.wrapper.slurm"
        elif self._config["queue_type"] == "LSF":
            class_name = "LsfCommands"
            module_name = "pysqa.wrapper.lsf"
        elif self._config["queue_type"] == "MOAB":
            class_name = "MoabCommands"
            module_name = "pysqa.wrapper.moab"
        elif self._config["queue_type"] == "GENT":
            class_name = "GentCommands"
            module_name = "pysqa.wrapper.gent"
        elif self._config["queue_type"] == "REMOTE":
            class_name = None
            module_name = None
        else:
            raise ValueError()
        if self._config["queue_type"] != "REMOTE":
            self._commands = getattr(importlib.import_module(module_name), class_name)()
        self._queues = Queues(self.queue_list)
        self._remote_flag = False
        self._ssh_delete_file_on_remote = True

    @property
    def ssh_delete_file_on_remote(self):
        return self._ssh_delete_file_on_remote

    @property
    def remote_flag(self):
        return self._remote_flag

    @property
    def config(self):
        """

        Returns:
            dict:
        """
        return self._config

    @property
    def queue_list(self):
        """

        Returns:
            list:
        """
        return list(self._config["queues"].keys())

    @property
    def queue_view(self):
        """

        Returns:
            pandas.DataFrame:
        """
        return pandas.DataFrame(self._config["queues"]).T.drop(
            ["script", "template"], axis=1
        )

    @property
    def queues(self):
        return self._queues

    def submit_job(
        self,
        queue=None,
        job_name=None,
        working_directory=None,
        cores=None,
        memory_max=None,
        run_time_max=None,
        command=None,
    ):
        """

        Args:
            queue (str/None):
            job_name (str/None):
            working_directory (str/None):
            cores (int/None):
            memory_max (int/None):
            run_time_max (int/None):
            command (str/None):

        Returns:
            int:
        """
        if " " in working_directory: 
            raise ValueError("Whitespaces in the working_directory name are not supported!")
        working_directory, queue_script_path = self._write_queue_script(
            queue=queue,
            job_name=job_name,
            working_directory=working_directory,
            cores=cores,
            memory_max=memory_max,
            run_time_max=run_time_max,
            command=command,
        )
        out = self._execute_command(
            commands=self._commands.submit_job_command + [queue_script_path],
            working_directory=working_directory,
            split_output=False,
        )
        if out is not None:
            return self._commands.get_job_id_from_output(out)
        else:
            return None

    def enable_reservation(self, process_id):
        """

        Args:
            process_id (int):

        Returns:
            str:
        """
        out = self._execute_command(
            commands=self._commands.enable_reservation_command + [str(process_id)],
            split_output=True,
        )
        if out is not None:
            return out[0]
        else:
            return None

    def delete_job(self, process_id):
        """

        Args:
            process_id (int):

        Returns:
            str:
        """
        out = self._execute_command(
            commands=self._commands.delete_job_command + [str(process_id)],
            split_output=True,
        )
        if out is not None:
            return out[0]
        else:
            return None

    def get_queue_status(self, user=None):
        """

        Args:
            user (str):

        Returns:
            pandas.DataFrame:
        """
        out = self._execute_command(
            commands=self._commands.get_queue_status_command, split_output=False
        )
        df = self._commands.convert_queue_status(queue_status_output=out)
        if user is None:
            return df
        else:
            return df[df["user"] == user]

    def get_status_of_my_jobs(self):
        """

        Returns:
           pandas.DataFrame:
        """
        return self.get_queue_status(user=self._get_user())

    def get_status_of_job(self, process_id):
        """

        Args:
            process_id:

        Returns:
             str: ['running', 'pending', 'error']
        """
        df = self.get_queue_status()
        df_selected = df[df["jobid"] == process_id]["status"]
        if len(df_selected) != 0:
            return df_selected.values[0]
        else:
            return None

    def get_status_of_jobs(self, process_id_lst):
        """

        Args:
            process_id_lst:

        Returns:
             list: ['running', 'pending', 'error', ...]
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

    def get_job_from_remote(self, working_directory, delete_remote=False):
        """
        Get the results of the calculation - this is necessary when the calculation was executed on a remote host.
        """
        pass

    def convert_path_to_remote(self, path):
        pass

    def transfer_file(self, file, transfer_back=False, delete_remote=False):
        pass

    def check_queue_parameters(
        self, queue, cores=1, run_time_max=None, memory_max=None, active_queue=None
    ):
        """

        Args:
            queue (str/None):
            cores (int):
            run_time_max (int/None):
            memory_max (int/None):
            active_queue (dict):

        Returns:
            list: [cores, run_time_max, memory_max]
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
        queue=None,
        job_name=None,
        working_directory=None,
        cores=None,
        memory_max=None,
        run_time_max=None,
        command=None,
    ):
        """

        Args:
            queue (str/None):
            job_name (str/None):
            working_directory (str/None):
            cores (int/None):
            memory_max (int/None):
            run_time_max (int/None):
            command (str/None):

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
            command=command,
        )
        if not os.path.exists(working_directory):
            os.makedirs(working_directory)
        queue_script_path = os.path.join(working_directory, "run_queue.sh")
        with open(queue_script_path, "w") as f:
            f.writelines(queue_script)
        return working_directory, queue_script_path

    def _job_submission_template(
        self,
        queue=None,
        job_name="job.py",
        working_directory=".",
        cores=None,
        memory_max=None,
        run_time_max=None,
        command=None,
    ):
        """

        Args:
            queue (str/None):
            job_name (str):
            working_directory (str):
            cores (int/None):
            memory_max (int/None):
            run_time_max (int/None):
            command (str/None):

        Returns:
            str:
        """
        if queue is None:
            queue = self._config["queue_primary"]
        self._value_error_if_none(value=command)
        if queue not in self.queue_list:
            raise ValueError()
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
        )

    @staticmethod
    def _get_user():
        """

        Returns:
            str:
        """
        return getpass.getuser()

    @staticmethod
    def _execute_command(commands, working_directory=None, split_output=True, shell=False):
        """

        Args:
            commands (list/str):
            working_directory (str):
            split_output (bool):
            shell (bool):

        Returns:
            str:
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
        except subprocess.CalledProcessError:
            out = None
        if out is not None and split_output:
            return out.split("\n")
        else:
            return out

    @staticmethod
    def _fill_queue_dict(queue_lst_dict):
        """

        Args:
            queue_lst_dict (dict):
        """
        queue_keys = ["cores_min", "cores_max", "run_time_max", "memory_max"]
        for queue_dict in queue_lst_dict.values():
            for key in set(queue_keys) - set(queue_dict.keys()):
                queue_dict[key] = None

    @staticmethod
    def _load_templates(queue_lst_dict, directory="."):
        """

        Args:
            queue_lst_dict (dict):
            directory (str):
        """
        for queue_dict in queue_lst_dict.values():
            if "script" in queue_dict.keys():
                with open(os.path.join(directory, queue_dict["script"]), "r") as f:
                    queue_dict["template"] = Template(f.read())

    @staticmethod
    def _value_error_if_none(value):
        """

        Args:
            value (str/None):
        """
        if value is None:
            raise ValueError()
        if not isinstance(value, str):
            raise TypeError()

    @classmethod
    def _value_in_range(cls, value, value_min=None, value_max=None):
        """

        Args:
            value (int/float/None):
            value_min (int/float/None):
            value_max (int/float/None):

        Returns:
            int/float/None:
        """

        if value is not None:
            value_, value_min_, value_max_ = [
                cls._memory_spec_string_to_value(v)
                if v is not None and isinstance(v, str)
                else v
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
    def _is_memory_string(value):
        """
        Tests a string if it specifies a certain amount of memory e.g.: '20G', '60b'. Also pure integer strings are
        also valid.

        Args:
            value (str): the string to test

        Returns:
            (bool): A boolean value if the string matches a memory specification
        """
        memory_spec_pattern = r"[0-9]+[bBkKmMgGtT]?"
        return re.findall(memory_spec_pattern, value)[0] == value

    @classmethod
    def _memory_spec_string_to_value(
        cls, value, default_magnitude="m", target_magnitude="b"
    ):
        """
        Converts a valid memory string (tested by _is_memory_string) into an integer/float value of desired
        magnitude `default_magnitude`. If it is a plain integer string (e.g.: '50000') it will be interpreted with
        the magnitude passed in by the `default_magnitude`. The output will rescaled to `target_magnitude`

        Args:
            value (str): the string
            default_magnitude (str): magnitude for interpreting plain integer strings [b, B, k, K, m, M, g, G, t, T]
            target_magnitude (str): to which the output value should be converted [b, B, k, K, m, M, g, G, t, T]

        Returns:
            (float/int): the value of the string in `target_magnitude` units
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
