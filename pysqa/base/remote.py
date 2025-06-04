import getpass
import json
import os
import warnings
from typing import Optional, Union

import pandas
import paramiko
from tqdm import tqdm

from pysqa.base.config import QueueAdapterWithConfig
from pysqa.base.core import execute_command


class RemoteQueueAdapter(QueueAdapterWithConfig):
    """
    A class representing a remote queue adapter.

    Args:
        config (dict): The configuration dictionary.
        directory (str, optional): The directory path. Defaults to "~/.queues".
        execute_command (callable, optional): The execute command function. Defaults to execute_command.

    Attributes:
        _ssh_host (str): The SSH host.
        _ssh_username (str): The SSH username.
        _ssh_known_hosts (str): The path to the known hosts file.
        _ssh_key (str): The path to the SSH key file.
        _ssh_ask_for_password (bool): Flag indicating whether to ask for SSH password.
        _ssh_password (str): The SSH password.
        _ssh_key_passphrase (str): The SSH key passphrase.
        _ssh_two_factor_authentication (bool): Flag indicating whether to use two-factor authentication.
        _ssh_authenticator_service (str): The SSH authenticator service.
        _ssh_proxy_host (str): The SSH proxy host.
        _ssh_remote_config_dir (str): The remote configuration directory.
        _ssh_remote_path (str): The remote path.
        _ssh_local_path (str): The local path.
        _ssh_delete_file_on_remote (bool): Flag indicating whether to delete files on the remote host.
        _ssh_port (int): The SSH port.
        _ssh_continous_connection (bool): Flag indicating whether to use continuous SSH connection.
        _ssh_connection (None or paramiko.SSHClient): The SSH connection object.
        _ssh_proxy_connection (None or paramiko.SSHClient): The SSH proxy connection object.
        _remote_flag (bool): Flag indicating whether the adapter is for remote queue.

    Methods:
        convert_path_to_remote(path: str) -> str:
            Converts a local path to a remote path.

        submit_job(queue: Optional[str] = None, job_name: Optional[str] = None, working_directory: Optional[str] = None,
                   cores: Optional[int] = None, memory_max: Optional[int] = None, run_time_max: Optional[int] = None,
                   dependency_list: Optional[list[str]] = None, command: Optional[str] = None, **kwargs) -> int:
            Submits a job to the remote queue.

        enable_reservation(process_id: int) -> str:
            Enables a reservation for a job.

        delete_job(process_id: int) -> str:
            Deletes a job from the remote queue.

        get_queue_status(user: Optional[str] = None) -> pandas.DataFrame:
            Retrieves the queue status.

        get_job_from_remote(working_directory: str):
            Retrieves the results of a calculation executed on a remote host.

        transfer_file(file: str, transfer_back: bool = False, delete_file_on_remote: bool = False):
            Transfers a file to/from the remote host.

        __del__():
            Closes the SSH connections.

        _check_ssh_connection():
            Checks if an SSH connection is open.

        _transfer_files(file_dict: dict, sftp=None, transfer_back: bool = False):
            Transfers files to/from the remote host.

        _open_ssh_connection() -> paramiko.SSHClient:
            Opens an SSH connection.
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
        self._ssh_host = config["ssh_host"]
        self._ssh_username = config["ssh_username"]
        self._ssh_known_hosts = os.path.abspath(
            os.path.expanduser(config["known_hosts"])
        )
        if "ssh_key" in config:
            self._ssh_key = os.path.abspath(os.path.expanduser(config["ssh_key"]))
            self._ssh_ask_for_password = False
        else:
            self._ssh_key = None
        self._ssh_password = config.get("ssh_password")
        if self._ssh_password is not None:
            self._ssh_ask_for_password = False
        else:
            self._ssh_ask_for_password = config.get("ssh_ask_for_password", False)
        self._ssh_key_passphrase = config.get("ssh_key_passphrase")
        self._ssh_two_factor_authentication = config.get(
            "ssh_two_factor_authentication", False
        )
        self._ssh_authenticator_service = config.get("ssh_authenticator_service")
        if self._ssh_authenticator_service is not None:
            self._ssh_two_factor_authentication = True
        self._ssh_proxy_host = config.get("ssh_proxy_host")
        self._ssh_remote_config_dir = config["ssh_remote_config_dir"]
        self._ssh_remote_path = config["ssh_remote_path"]
        self._ssh_local_path = os.path.abspath(
            os.path.expanduser(config["ssh_local_path"])
        )
        self._ssh_delete_file_on_remote = config.get("ssh_delete_file_on_remote", True)
        self._ssh_port = config.get("ssh_port", 22)
        self._ssh_continous_connection = config.get("ssh_continous_connection", False)
        self._ssh_connection = None
        self._ssh_proxy_connection = None
        self._python_executable = config.get("python_executable", "python")
        self._remote_flag = True

    def convert_path_to_remote(self, path: str) -> str:
        """
        Converts a local path to a remote path.

        Args:
            path (str): The local path.

        Returns:
            str: The remote path.
        """
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
        Submits a job to the remote queue.

        Args:
            queue (str, optional): The queue name.
            job_name (str, optional): The job name.
            working_directory (str, optional): The working directory.
            cores (int, optional): The number of cores.
            memory_max (int, optional): The maximum memory.
            run_time_max (int, optional): The maximum run time.
            dependency_list (list[str], optional): The list of job dependencies.
            command (str, optional): The command to execute.

        Returns:
            int: The process ID of the submitted job.
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
        Enables a reservation for a job.

        Args:
            process_id (int): The process ID.

        Returns:
            str: The output of the reservation command.
        """
        return self._execute_remote_command(
            command=self._reservation_command(job_id=process_id)
        )

    def delete_job(self, process_id: int) -> str:
        """
        Deletes a job from the remote queue.

        Args:
            process_id (int): The process ID.

        Returns:
            str: The output of the delete command.
        """
        return self._execute_remote_command(
            command=self._delete_command(job_id=process_id)
        )

    def get_queue_status(self, user: Optional[str] = None) -> pandas.DataFrame:
        """
        Retrieves the queue status.

        Args:
            user (str, optional): The username.

        Returns:
            pandas.DataFrame: The queue status.
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
        Retrieves the results of a calculation executed on a remote host.

        Args:
            working_directory (str): The local working directory.
        """
        working_directory = os.path.abspath(os.path.expanduser(working_directory))
        remote_working_directory = self._get_remote_working_dir(
            working_directory=working_directory
        )
        remote_dict = json.loads(
            self._execute_remote_command(
                command=self._python_executable
                + " -m pysqa --list --working_directory "
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
        """
        Transfers a file to/from the remote host.

        Args:
            file (str): The file path.
            transfer_back (bool, optional): Flag indicating whether to transfer the file back to the local host.
            delete_file_on_remote (bool, optional): Flag indicating whether to delete the file on the remote host.
        """
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
        """
        Closes the SSH connections.
        """
        if self._ssh_connection is not None:
            self._ssh_connection.close()
        if self._ssh_proxy_connection is not None:
            self._ssh_proxy_connection.close()

    def _check_ssh_connection(self):
        """
        Checks if an SSH connection is open.
        """
        if self._ssh_connection is None:
            self._ssh_connection = self._open_ssh_connection()

    def _transfer_files(self, file_dict: dict, sftp=None, transfer_back: bool = False):
        """
        Transfers files to/from the remote host.

        Args:
            file_dict (dict): The dictionary containing the file paths.
            sftp (None or paramiko.SFTPClient, optional): The SFTP client object.
            transfer_back (bool, optional): Flag indicating whether to transfer the files back to the local host.
        """
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

    def _open_ssh_connection(self) -> paramiko.SSHClient:
        """
        Opens an SSH connection.

        Returns:
            paramiko.SSHClient: The SSH connection object.
        """
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

    def _remote_command(self) -> str:
        """
        Returns the command to execute on the remote host.

        Returns:
            str: The remote command.
        """
        return (
            self._python_executable
            + " -m pysqa --config_directory "
            + self._ssh_remote_config_dir
            + " "
        )

    def _get_queue_status_command(self) -> str:
        """
        Returns the command to get the queue status on the remote host.

        Returns:
            str: The queue status command.
        """
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
    ) -> str:
        """
        Generates the command to submit a job to the remote host.

        Args:
            queue (str, optional): The queue to submit the job to.
            job_name (str, optional): The name of the job.
            working_directory (str, optional): The working directory for the job.
            cores (int, optional): The number of cores required for the job.
            memory_max (int, optional): The maximum memory required for the job.
            run_time_max (int, optional): The maximum run time for the job.
            command_str (str, optional): The command to be executed by the job.

        Returns:
            str: The submit command.
        """
        command = self._remote_command() + "--submit "
        if queue is not None:
            command += "--queue " + queue + " "
        if job_name is not None:
            command += "--job_name " + job_name + " "
        if working_directory is not None:
            command += "--working_directory " + working_directory + " "
        if cores is not None:
            command += "--cores " + str(cores) + " "
        if memory_max is not None:
            command += "--memory " + str(memory_max) + " "
        if run_time_max is not None:
            command += "--run_time " + str(run_time_max) + " "
        if command_str is not None:
            command += '--command "' + command_str + '" '
        return command

    def _delete_command(self, job_id: int) -> str:
        """
        Generates the command to delete a job on the remote host.

        Args:
            job_id (int): The ID of the job to delete.

        Returns:
            str: The delete command.
        """
        return self._remote_command() + "--delete --id " + str(job_id)

    def _reservation_command(self, job_id: int) -> str:
        """
        Generates the command to reserve a job on the remote host.

        Args:
            job_id (int): The ID of the job to reserve.

        Returns:
            str: The reservation command.
        """
        return self._remote_command() + "--reservation --id " + str(job_id)

    def _execute_remote_command(self, command: str) -> str:
        """
        Executes a remote command on the SSH connection.

        Args:
            command (str): The command to execute.

        Returns:
            str: The output of the command.
        """
        if self._ssh_continous_connection:
            self._check_ssh_connection()
            ssh = self._ssh_connection
        else:
            ssh = self._open_ssh_connection()
        stdin, stdout, stderr = ssh.exec_command(command)
        warnings.warn(message=stderr.read().decode(), stacklevel=2)
        output = stdout.read().decode()
        if not self._ssh_continous_connection:
            ssh.close()
        return output

    def _get_remote_working_dir(self, working_directory: str) -> str:
        """
        Get the remote working directory path.

        Args:
            working_directory (str): The local working directory path.

        Returns:
            str: The remote working directory path.
        """
        return os.path.join(
            self._ssh_remote_path,
            os.path.relpath(working_directory, self._ssh_local_path),
        )

    def _create_remote_dir(self, directory: Union[str, list[str]]) -> None:
        """
        Creates a remote directory on the SSH server.

        Args:
            directory (Union[str, List[str]]): The directory or list of directories to create.

        Raises:
            TypeError: If the directory argument is not a string or a list.
        """
        if isinstance(directory, str):
            self._execute_remote_command(command="mkdir -p " + directory)
        elif isinstance(directory, list):
            command = "mkdir -p "
            for d in directory:
                command += d + " "
            self._execute_remote_command(command=command)
        else:
            raise TypeError("Invalid directory argument type.")

    def _transfer_data_to_remote(self, working_directory: str) -> None:
        """
        Transfers data from the local machine to the remote host.

        Args:
            working_directory (str): The local working directory path.

        Returns:
            None
        """
        working_directory = os.path.abspath(os.path.expanduser(working_directory))
        remote_working_directory = self._get_remote_working_dir(
            working_directory=working_directory
        )
        file_dict = {}
        new_dir_list = []
        for p, _folder, files in os.walk(working_directory):
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
        Get the username used for SSH connection.

        Returns:
            str: The username.
        """
        return self._ssh_username

    @staticmethod
    def _get_file_transfer(file: str, local_dir: str, remote_dir: str) -> str:
        """
        Get the absolute path of the file on the remote host.

        Args:
            file (str): The file path.
            local_dir (str): The local working directory path.
            remote_dir (str): The remote working directory path.

        Returns:
            str: The absolute path of the file on the remote host.
        """
        return os.path.abspath(
            os.path.join(remote_dir, os.path.relpath(file, local_dir))
        )
