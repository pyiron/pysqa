# coding: utf-8
# Copyright (c) Jan Janssen

import getpass
import json
import os
import warnings
from typing import Optional

import pandas
import paramiko
from tqdm import tqdm

from pysqa.utils.basic import BasisQueueAdapter
from pysqa.utils.execute import execute_command


class RemoteQueueAdapter(BasisQueueAdapter):
    def __init__(
        self,
        config: dict,
        directory: str = "~/.queues",
        execute_command: callable = execute_command,
    ):
        super(RemoteQueueAdapter, self).__init__(
            config=config, directory=directory, execute_command=execute_command
        )
        self._ssh_host = config["ssh_host"]
        self._ssh_username = config["ssh_username"]
        self._ssh_known_hosts = os.path.abspath(
            os.path.expanduser(config["known_hosts"])
        )
        if "ssh_key" in config.keys():
            self._ssh_key = os.path.abspath(os.path.expanduser(config["ssh_key"]))
            self._ssh_ask_for_password = False
        else:
            self._ssh_key = None
        if "ssh_password" in config.keys():
            self._ssh_password = config["ssh_password"]
            self._ssh_ask_for_password = False
        else:
            self._ssh_password = None
        if "ssh_ask_for_password" in config.keys():
            self._ssh_ask_for_password = config["ssh_ask_for_password"]
        else:
            self._ssh_ask_for_password = False
        if "ssh_key_passphrase" in config.keys():
            self._ssh_key_passphrase = config["ssh_key_passphrase"]
        else:
            self._ssh_key_passphrase = None
        if "ssh_two_factor_authentication" in config.keys():
            self._ssh_two_factor_authentication = config[
                "ssh_two_factor_authentication"
            ]
        else:
            self._ssh_two_factor_authentication = False
        if "ssh_authenticator_service" in config.keys():
            self._ssh_authenticator_service = config["ssh_authenticator_service"]
            self._ssh_two_factor_authentication = True
        else:
            self._ssh_authenticator_service = None
        if "ssh_proxy_host" in config.keys():
            self._ssh_proxy_host = config["ssh_proxy_host"]
        else:
            self._ssh_proxy_host = None
        self._ssh_remote_config_dir = config["ssh_remote_config_dir"]
        self._ssh_remote_path = config["ssh_remote_path"]
        self._ssh_local_path = os.path.abspath(
            os.path.expanduser(config["ssh_local_path"])
        )
        if "ssh_delete_file_on_remote" in config.keys():
            self._ssh_delete_file_on_remote = config["ssh_delete_file_on_remote"]
        else:
            self._ssh_delete_file_on_remote = True
        if "ssh_port" in config.keys():
            self._ssh_port = config["ssh_port"]
        else:
            self._ssh_port = 22
        if "ssh_continous_connection" in config.keys():
            self._ssh_continous_connection = config["ssh_continous_connection"]
        else:
            self._ssh_continous_connection = False
        self._ssh_connection = None
        self._ssh_proxy_connection = None
        self._remote_flag = True

    def convert_path_to_remote(self, path: str):
        working_directory = os.path.abspath(os.path.expanduser(path))
        return self._get_remote_working_dir(working_directory=working_directory)

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
        **kwargs,
    ) -> int:
        """

        Args:
            queue (str/None):
            job_name (str/None):
            working_directory (str/None):
            cores (int/None):
            memory_max (int/None):
            run_time_max (int/None):
            dependency_list (list/None):
            command (str/None):

        Returns:
            int:
        """
        if dependency_list is not None:
            raise NotImplementedError(
                "Submitting jobs with dependencies to a remote cluster is not yet supported."
            )
        self._transfer_data_to_remote(working_directory=working_directory)
        output = self._execute_remote_command(command=command)
        return int(output.split()[-1])

    def enable_reservation(self, process_id: int) -> str:
        """

        Args:
            process_id (int):

        Returns:
            str:
        """
        return self._execute_remote_command(
            command=self._reservation_command(job_id=process_id)
        )

    def delete_job(self, process_id: int) -> str:
        """

        Args:
            process_id (int):

        Returns:
            str:
        """
        return self._execute_remote_command(
            command=self._delete_command(job_id=process_id)
        )

    def get_queue_status(self, user: Optional[str] = None) -> pandas.DataFrame:
        """

        Args:
            user (str):

        Returns:
            pandas.DataFrame:
        """
        df = pandas.DataFrame(
            json.loads(
                self._execute_remote_command(command=self._get_queue_status_command())
            )
        )
        if user is None:
            return df
        else:
            return df[df["user"] == user]

    def get_job_from_remote(self, working_directory: str):
        """
        Get the results of the calculation - this is necessary when the calculation was executed on a remote host.
        """
        working_directory = os.path.abspath(os.path.expanduser(working_directory))
        remote_working_directory = self._get_remote_working_dir(
            working_directory=working_directory
        )
        remote_dict = json.loads(
            self._execute_remote_command(
                command="python -m pysqa --list --working_directory "
                + remote_working_directory
            )
        )
        for d in remote_dict["dirs"]:
            local_dir = self._get_file_transfer(
                file=d, local_dir=remote_working_directory, remote_dir=working_directory
            )
            os.makedirs(local_dir, exist_ok=True)
        file_dict = {}
        for f in remote_dict["files"]:
            local_file = self._get_file_transfer(
                file=f, local_dir=remote_working_directory, remote_dir=working_directory
            )
            file_dict[local_file] = f
        self._transfer_files(file_dict=file_dict, sftp=None, transfer_back=True)
        if self._ssh_delete_file_on_remote:
            self._execute_remote_command(command="rm -r " + remote_working_directory)

    def transfer_file(
        self,
        file: str,
        transfer_back: bool = False,
        delete_file_on_remote: bool = False,
    ):
        working_directory = os.path.abspath(os.path.expanduser(file))
        remote_working_directory = self._get_remote_working_dir(
            working_directory=working_directory
        )
        self._create_remote_dir(directory=os.path.dirname(remote_working_directory))
        self._transfer_files(
            file_dict={working_directory: remote_working_directory},
            sftp=None,
            transfer_back=transfer_back,
        )
        if self._ssh_delete_file_on_remote and transfer_back and delete_file_on_remote:
            self._execute_remote_command(command="rm " + remote_working_directory)

    def __del__(self):
        if self._ssh_connection is not None:
            self._ssh_connection.close()
        if self._ssh_proxy_connection is not None:
            self._ssh_proxy_connection.close()

    def _check_ssh_connection(self):
        if self._ssh_connection is None:
            self._ssh_connection = self._open_ssh_connection()

    def _transfer_files(self, file_dict: dict, sftp=None, transfer_back: bool = False):
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
                    # Check remote file existence.
                    # If the remote file does not exist, sftp_client.get() will make the local file empty
                    # sftp_client.stat() can throw an exception early to prevent the execution of sftp_client.get().
                    sftp_client.stat(file_dst)
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
        if (
            self._ssh_key is not None
            and self._ssh_key_passphrase is not None
            and not self._ssh_ask_for_password
        ):
            ssh.connect(
                hostname=self._ssh_host,
                port=self._ssh_port,
                username=self._ssh_username,
                key_filename=self._ssh_key,
                passphrase=self._ssh_key_passphrase,
            )
        elif self._ssh_key is not None and not self._ssh_ask_for_password:
            ssh.connect(
                hostname=self._ssh_host,
                port=self._ssh_port,
                username=self._ssh_username,
                key_filename=self._ssh_key,
            )
        elif (
            self._ssh_password is not None
            and self._ssh_authenticator_service is None
            and not self._ssh_two_factor_authentication
            and not self._ssh_ask_for_password
        ):
            ssh.connect(
                hostname=self._ssh_host,
                port=self._ssh_port,
                username=self._ssh_username,
                password=self._ssh_password,
            )
        elif self._ssh_ask_for_password and not self._ssh_two_factor_authentication:
            ssh.connect(
                hostname=self._ssh_host,
                port=self._ssh_port,
                username=self._ssh_username,
                password=getpass.getpass(prompt="SSH Password: ", stream=None),
            )
        elif (
            self._ssh_password is not None
            and self._ssh_authenticator_service is not None
            and self._ssh_two_factor_authentication
        ):

            def authentication(title, instructions, prompt_list):
                from pyauthenticator import get_two_factor_code

                if len(prompt_list) > 0:
                    return [
                        get_two_factor_code(service=self._ssh_authenticator_service)
                    ]
                else:
                    return []

            ssh.connect(
                hostname=self._ssh_host,
                port=self._ssh_port,
                username=self._ssh_username,
                password=self._ssh_password,
            )

            ssh._transport.auth_interactive(
                username=self._ssh_username, handler=authentication, submethods=""
            )
        elif (
            self._ssh_password is not None
            and self._ssh_authenticator_service is None
            and self._ssh_two_factor_authentication
        ):
            ssh.connect(
                hostname=self._ssh_host,
                port=self._ssh_port,
                username=self._ssh_username,
                password=self._ssh_password,
            )
            ssh._transport.auth_interactive_dumb(
                username=self._ssh_username, handler=None, submethods=""
            )
        elif self._ssh_ask_for_password and self._ssh_two_factor_authentication:
            ssh.connect(
                hostname=self._ssh_host,
                port=self._ssh_port,
                username=self._ssh_username,
                password=getpass.getpass(prompt="SSH Password: ", stream=None),
            )
            ssh._transport.auth_interactive_dumb(
                username=self._ssh_username, handler=None, submethods=""
            )
        else:
            raise ValueError("Un-supported authentication method.")

        if self._ssh_proxy_host is not None:
            client_new = paramiko.SSHClient()
            client_new.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            vmtransport = ssh.get_transport()
            vmchannel = vmtransport.open_channel(
                kind="direct-tcpip",
                dest_addr=(self._ssh_proxy_host, self._ssh_port),
                src_addr=(self._ssh_host, self._ssh_port),
            )
            client_new.connect(
                hostname=self._ssh_proxy_host,
                username=self._ssh_username,
                sock=vmchannel,
            )
            self._ssh_proxy_connection = ssh
            return client_new
        else:
            return ssh

    def _remote_command(self):
        return "python -m pysqa --config_directory " + self._ssh_remote_config_dir + " "

    def _get_queue_status_command(self):
        return self._remote_command() + "--status"

    def _submit_command(
        self,
        queue: Optional[str] = None,
        job_name: Optional[str] = None,
        working_directory: Optional[str] = None,
        cores: Optional[int] = None,
        memory_max: Optional[int] = None,
        run_time_max: Optional[int] = None,
        command_str: Optional[str] = None,
    ):
        command = self._remote_command() + "--submit "
        if queue is not None:
            command += "--queue " + queue + " "
        if job_name is not None:
            command += "--job_name " + job_name + " "
        if working_directory is not None:
            command += "--working_directory " + working_directory + " "
        if cores is not None:
            command += "--cores " + cores + " "
        if memory_max is not None:
            command += "--memory " + memory_max + " "
        if run_time_max is not None:
            command += "--run_time " + run_time_max + " "
        if command_str is not None:
            command += '--command "' + command_str + '" '
        return command

    def _delete_command(self, job_id: int) -> str:
        return self._remote_command() + "--delete --id " + str(job_id)

    def _reservation_command(self, job_id: int) -> str:
        return self._remote_command() + "--reservation --id " + str(job_id)

    def _execute_remote_command(self, command: str):
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

    def _get_remote_working_dir(self, working_directory: str):
        return os.path.join(
            self._ssh_remote_path,
            os.path.relpath(working_directory, self._ssh_local_path),
        )

    def _create_remote_dir(self, directory: str):
        if isinstance(directory, str):
            self._execute_remote_command(command="mkdir -p " + directory)
        elif isinstance(directory, list):
            command = "mkdir -p "
            for d in directory:
                command += d + " "
            self._execute_remote_command(command=command)
        else:
            raise TypeError()

    def _transfer_data_to_remote(self, working_directory: str):
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
                    remote_dir=remote_working_directory,
                )
            )
            for f in files:
                file_path = os.path.join(p, f)
                file_dict[file_path] = self._get_file_transfer(
                    file=file_path,
                    local_dir=working_directory,
                    remote_dir=remote_working_directory,
                )
        self._create_remote_dir(directory=new_dir_list)
        self._transfer_files(file_dict=file_dict, sftp=None, transfer_back=False)

    def _get_user(self) -> str:
        """

        Returns:
            str:
        """
        return self._ssh_username

    @staticmethod
    def _get_file_transfer(file: str, local_dir: str, remote_dir: str) -> str:
        return os.path.abspath(
            os.path.join(remote_dir, os.path.relpath(file, local_dir))
        )
