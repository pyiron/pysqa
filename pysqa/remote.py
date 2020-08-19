# coding: utf-8
# Copyright (c) Jan Janssen

import json
import os
import pandas
import paramiko
import warnings
from tqdm import tqdm
from pysqa.basic import BasisQueueAdapter


class RemoteQueueAdapter(BasisQueueAdapter):
    def __init__(self, config, directory="~/.queues"):
        super(RemoteQueueAdapter, self).__init__(config=config, directory=directory)
        self._ssh_host = config['ssh_host']
        self._ssh_username = config['ssh_username']
        self._ssh_known_hosts = os.path.abspath(os.path.expanduser(config['known_hosts']))
        self._ssh_key = os.path.abspath(os.path.expanduser(config['ssh_key']))
        self._ssh_remote_config_dir = config['ssh_remote_config_dir']
        self._ssh_remote_path = config['ssh_remote_path']
        self._ssh_local_path = os.path.abspath(os.path.expanduser(config['ssh_local_path']))
        if 'ssh_delete_file_on_remote' in config.keys():
            self._ssh_delete_file_on_remote = config['ssh_delete_file_on_remote']
        else:
            self._ssh_delete_file_on_remote = True
        if 'ssh_port' in config.keys():
            self._ssh_port = config['ssh_port']
        else:
            self._ssh_port = 22
        self._ssh_continous_connection = 'ssh_continous_connection' in config.keys()
        self._ssh_connection = None
        self._remote_flag = True
        
    def convert_path_to_remote(self, path):
        working_directory = os.path.abspath(os.path.expanduser(path))
        return self._get_remote_working_dir(
            working_directory=working_directory
        )

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
        self._transfer_data_to_remote(working_directory=working_directory)
        output = self._execute_remote_command(command=command)
        return int(output.split()[-1])

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

    def get_job_from_remote(self, working_directory, delete_remote=False):
        """
        Get the results of the calculation - this is necessary when the calculation was executed on a remote host.
        """
        working_directory = os.path.abspath(os.path.expanduser(working_directory))
        remote_working_directory = self._get_remote_working_dir(
            working_directory=working_directory
        )
        remote_dict = json.loads(
            self._execute_remote_command(
                command='python -m pysqa.cmd --list --working_directory ' + remote_working_directory
            )
        )
        for d in remote_dict['dirs']:
            local_dir = self._get_file_transfer(
                file=d,
                local_dir=remote_working_directory,
                remote_dir=working_directory
            )
            os.makedirs(local_dir, exist_ok=True)
        file_dict = {}
        for f in remote_dict['files']:
            local_file = self._get_file_transfer(
                file=f,
                local_dir=remote_working_directory,
                remote_dir=working_directory
            )
            file_dict[local_file] = f
        self._transfer_files(file_dict=file_dict, sftp=None, transfer_back=True)
        if delete_remote:
            self._execute_remote_command(
                command="rm -r " + remote_working_directory
            )

    def transfer_file(self, file, transfer_back=False, delete_remote=False):
        working_directory = os.path.abspath(os.path.expanduser(file))
        remote_working_directory = self._get_remote_working_dir(
            working_directory=working_directory
        )
        self._create_remote_dir(directory=os.path.dirname(remote_working_directory))
        self._transfer_files(file_dict={working_directory: remote_working_directory},
                             sftp=None,
                             transfer_back=transfer_back)
        if delete_remote and transfer_back:
            self._execute_remote_command(
                command="rm " + remote_working_directory
            )

    def __del__(self):
        if self._ssh_connection is not None:
            self._ssh_connection.close()

    def _check_ssh_connection(self):
        if self._ssh_connection is None:
            self._ssh_connection = self._open_ssh_connection()

    def _transfer_files(self, file_dict, sftp=None, transfer_back=False):
        if sftp is None:
            if self._ssh_continous_connection:
                self._check_ssh_connection()
                ssh = self._ssh_connection
            else:
                ssh = self._open_ssh_connection()
            sftp_client = ssh.open_sftp()
        else:
            sftp_client = sftp
        for file_src, file_dst in tqdm(file_dict.items()):
            if transfer_back:
                try:
                    sftp_client.get(file_dst, file_src)
                except FileNotFoundError:
                    pass
            else:
                sftp_client.put(file_src, file_dst)
        if sftp is None:
            sftp_client.close()

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
            self._check_ssh_connection()
            ssh = self._ssh_connection
        else:
            ssh = self._open_ssh_connection()
        stdin, stdout, stderr = ssh.exec_command(command)
        warnings.warn(stderr.read().decode())
        output = stdout.read().decode()
        if not self._ssh_continous_connection:
            ssh.close()
        return output

    def _get_remote_working_dir(self, working_directory):
        return os.path.join(
            self._ssh_remote_path,
            os.path.relpath(
                working_directory,
                self._ssh_local_path
            )
        )

    def _create_remote_dir(self, directory):
        if isinstance(directory, str):
            self._execute_remote_command(
                command="mkdir -p " + directory
            )
        elif isinstance(directory, list):
            command = "mkdir -p "
            for d in directory:
                command += d + " "
            self._execute_remote_command(
                command=command
            )
        else:
            raise TypeError()

    def _transfer_data_to_remote(self, working_directory):
        working_directory = os.path.abspath(os.path.expanduser(working_directory))
        remote_working_directory = self._get_remote_working_dir(
            working_directory=working_directory
        )
        file_dict = {}
        new_dir_list = []
        for p, folder, files in os.walk(working_directory):
            new_dir_list.append(
                self._get_file_transfer(
                    file=p,
                    local_dir=working_directory,
                    remote_dir=remote_working_directory
                )
            )
            for f in files:
                file_path = os.path.join(p, f)
                file_dict[file_path] = self._get_file_transfer(
                    file=file_path,
                    local_dir=working_directory,
                    remote_dir=remote_working_directory)
        self._create_remote_dir(directory=new_dir_list)
        self._transfer_files(file_dict=file_dict, sftp=None, transfer_back=False)

    @staticmethod
    def _get_file_transfer(file, local_dir, remote_dir):
        return os.path.abspath(os.path.join(remote_dir, os.path.relpath(file, local_dir)))
