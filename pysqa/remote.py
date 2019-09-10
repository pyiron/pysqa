# coding: utf-8
# Copyright (c) Jan Janssen

import json
import pandas
import paramiko
from pysqa.basic import BasisQueueAdapter


class RemoteQueueAdapter(BasisQueueAdapter):
    def __init__(self, config, directory="~/.queues"):
        super(RemoteQueueAdapter, self).__init__(config=config, directory=directory)
        self._ssh_host = config['ssh_host']
        self._ssh_username = config['ssh_username']
        self._ssh_known_hosts = config['known_hosts']
        self._ssh_key = config['ssh_key']
        self._ssh_remote_config_dir = config['ssh_remote_config_dir']
        if 'ssh_port' in config.keys():
            self._ssh_port = config['ssh_port']
        else:
            self._ssh_port = 22
        self._ssh_continous_connection = 'ssh_continous_connection' in config.keys()
        if self._ssh_continous_connection:
            self._ssh_connection = self._open_ssh_connection()
        else:
            self._ssh_connection = None

    def _open_ssh_connection(self):
        ssh = paramiko.SSHClient()
        ssh.load_host_keys(self._ssh_known_hosts)
        ssh.connect(hostname=self._ssh_host,
                    port=self._ssh_port,
                    username=self._ssh_username,
                    key_filename=self._ssh_key)
        return ssh

    def _remote_command(self):
        return 'python -m pysqa.cmd --config_directory ' + self._ssh_remote_config_dir + ' '

    def _get_queue_status_command(self):
        return self._remote_command() + '--status'

    def _submit_command(
            self,
            queue=None,
            job_name=None,
            working_directory=None,
            cores=None,
            memory_max=None,
            run_time_max=None,
            command_str=None
    ):
        command = self._remote_command() + '--submit '
        if queue is not None:
            command += '--queue ' + queue + ' '
        if job_name is not None:
            command += '--job_name ' + job_name + ' '
        if working_directory is not None:
            command += '--working_directory ' + working_directory + ' '
        if cores is not None:
            command += '--cores ' + cores + ' '
        if memory_max is not None:
            command += '--memory ' + memory_max + ' '
        if run_time_max is not None:
            command += '--run_time ' + run_time_max + ' '
        if command_str is not None:
            command += '--command "' + command_str + '" '
        return command

    def _delete_command(self, job_id):
        return self._remote_command() + '--delete --id ' + str(job_id)

    def _reservation_command(self, job_id):
        return self._remote_command() + '--reservation --id ' + str(job_id)

    def _execute_remote_command(self, command):
        if self._ssh_continous_connection:
            ssh = self._ssh_connection
        else:
            ssh = self._open_ssh_connection()
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        if not self._ssh_continous_connection:
            ssh.close()
        return output

    def __del__(self):
        self._ssh_connection.close()

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
        return int(
            self._execute_remote_command(
                command=self._submit_command(
                    queue=queue,
                    job_name=job_name,
                    working_directory=working_directory,
                    cores=cores,
                    memory_max=memory_max,
                    run_time_max=run_time_max,
                    command_str=command
                )
            )
        )

    def enable_reservation(self, process_id):
        """

        Args:
            process_id (int):

        Returns:
            str:
        """
        return self._execute_remote_command(
            command=self._reservation_command(
                job_id=process_id
            )
        )

    def delete_job(self, process_id):
        """

        Args:
            process_id (int):

        Returns:
            str:
        """
        return self._execute_remote_command(
            command=self._delete_command(
                job_id=process_id
            )
        )

    def get_queue_status(self, user=None):
        """

        Args:
            user (str):

        Returns:
            pandas.DataFrame:
        """
        df = pandas.DataFrame(
            json.loads(
                self._execute_remote_command(
                    command=self._get_queue_status_command()
                )
            )
        )
        if user is None:
            return df
        else:
            return df[df["user"] == user]

    def get_job_from_remote(self):
        """
        Get the results of the calculation - this is necessary when the calculation was executed on a remote host.
        """
        pass