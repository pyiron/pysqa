# coding: utf-8
# Copyright (c) Jan Janssen

import pandas
from pysqa.basic import BasisQueueAdapter


class ModularQueueAdapter(BasisQueueAdapter):
    def __init__(self, config, directory="~/.queues"):
        super(ModularQueueAdapter, self).__init__(config=config, directory=directory)
        self._queue_to_cluster_dict = {
            k: v["cluster"] for k, v in self._config["queues"].items()
        }
        for v in self._queue_to_cluster_dict.values():
            if v not in self._config["cluster"]:
                raise ValueError()

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
        working_directory, queue_script_path = self._write_queue_script(
            queue=queue,
            job_name=job_name,
            working_directory=working_directory,
            cores=cores,
            memory_max=memory_max,
            run_time_max=run_time_max,
            command=command,
        )
        cluster_module = self._queue_to_cluster_dict[queue]
        commands = (
            self._switch_cluster_command(cluster_module=cluster_module)
            + self._commands.submit_job_command
            + [queue_script_path]
        )
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

    def enable_reservation(self, process_id):
        """

        Args:
            process_id (int):

        Returns:
            str:
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

    def delete_job(self, process_id):
        """

        Args:
            process_id (int):

        Returns:
            str:
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

    def get_queue_status(self, user=None):
        """

        Args:
            user (str):

        Returns:
            pandas.DataFrame:
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
        df = pandas.concat(df_lst, axis=1, sort=False).reset_index(drop=True)
        if user is None:
            return df
        else:
            return df[df["user"] == user]

    @staticmethod
    def _resolve_queue_id(process_id, cluster_dict):
        cluster_queue_id = int(process_id / 10)
        cluster_module = cluster_dict[process_id - cluster_queue_id * 10]
        return cluster_module, cluster_queue_id

    @staticmethod
    def _switch_cluster_command(cluster_module):
        return ["module", "--quiet", "swap", "cluster/{};".format(cluster_module)]
