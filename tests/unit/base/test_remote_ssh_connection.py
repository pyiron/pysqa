import os
import unittest
from unittest.mock import MagicMock, patch

from pysqa import QueueAdapter

try:
    import paramiko
    from tqdm import tqdm
    from pysqa.base.remote import get_transport

    skip_remote_test = False
except ImportError:
    skip_remote_test = True


class FakeSSH:
    @staticmethod
    def get_transport(*args, **kwargs):
        return None


def _new_remote(directory_name):
    path = os.path.dirname(os.path.abspath(__file__))
    return QueueAdapter(directory=os.path.join(path, "../../static", directory_name))


@unittest.skipIf(
    skip_remote_test,
    "Either paramiko or tqdm are not installed, so the remote queue adapter tests are skipped.",
)
class TestGetTransport(unittest.TestCase):
    """Pure unit tests for get_transport(), without any network access."""

    def test_get_transport_returns_transport(self):
        ssh = MagicMock()
        ssh.get_transport.return_value = "a-transport"
        self.assertEqual(get_transport(ssh=ssh), "a-transport")

    def test_get_transport_raises_value_error_when_missing(self):
        with self.assertRaises(ValueError):
            get_transport(ssh=FakeSSH())


@unittest.skipIf(
    skip_remote_test,
    "Either paramiko or tqdm are not installed, so the remote queue adapter tests are skipped.",
)
class TestOpenSSHConnection(unittest.TestCase):
    """Unit tests for the authentication branches of _open_ssh_connection().

    paramiko.SSHClient is mocked out entirely, so these tests never touch the
    network - unlike the TestRemoteQueueAdapterRebex tests which connect to
    test.rebex.net and therefore require network access plus a known_hosts
    entry that matches the CI setup.
    """

    def test_key_with_passphrase(self):
        remote = _new_remote("remote")
        remote._adapter._ssh_key_passphrase = "secret"
        with patch("pysqa.base.remote.paramiko.SSHClient") as mock_cls:
            mock_ssh = MagicMock()
            mock_cls.return_value = mock_ssh
            result = remote._adapter._open_ssh_connection()
        self.assertIs(result, mock_ssh)
        mock_ssh.connect.assert_called_once_with(
            hostname="hpc-cluster.university.edu",
            port=22,
            username="hpcuser",
            key_filename=remote._adapter._ssh_key,
            passphrase="secret",
        )

    def test_key_without_passphrase(self):
        remote = _new_remote("remote")
        with patch("pysqa.base.remote.paramiko.SSHClient") as mock_cls:
            mock_ssh = MagicMock()
            mock_cls.return_value = mock_ssh
            result = remote._adapter._open_ssh_connection()
        self.assertIs(result, mock_ssh)
        mock_ssh.connect.assert_called_once_with(
            hostname="hpc-cluster.university.edu",
            port=22,
            username="hpcuser",
            key_filename=remote._adapter._ssh_key,
        )

    def test_password_auth(self):
        remote = _new_remote("remote")
        remote._adapter._ssh_key = None
        remote._adapter._ssh_password = "test1234"
        with patch("pysqa.base.remote.paramiko.SSHClient") as mock_cls:
            mock_ssh = MagicMock()
            mock_cls.return_value = mock_ssh
            result = remote._adapter._open_ssh_connection()
        self.assertIs(result, mock_ssh)
        mock_ssh.connect.assert_called_once_with(
            hostname="hpc-cluster.university.edu",
            port=22,
            username="hpcuser",
            password="test1234",
            look_for_keys=False,
        )

    def test_ask_for_password(self):
        remote = _new_remote("remote")
        remote._adapter._ssh_key = None
        remote._adapter._ssh_password = None
        remote._adapter._ssh_ask_for_password = True
        with (
            patch("pysqa.base.remote.paramiko.SSHClient") as mock_cls,
            patch(
                "pysqa.base.remote.getpass.getpass", return_value="typed-password"
            ) as mock_getpass,
        ):
            mock_ssh = MagicMock()
            mock_cls.return_value = mock_ssh
            result = remote._adapter._open_ssh_connection()
        self.assertIs(result, mock_ssh)
        mock_getpass.assert_called_once()
        mock_ssh.connect.assert_called_once_with(
            hostname="hpc-cluster.university.edu",
            port=22,
            username="hpcuser",
            password="typed-password",
        )

    def test_two_factor_with_authenticator_service(self):
        remote = _new_remote("remote_alternative")
        self.assertTrue(remote._adapter._ssh_two_factor_authentication)
        with patch("pysqa.base.remote.paramiko.SSHClient") as mock_cls:
            mock_ssh = MagicMock()
            mock_cls.return_value = mock_ssh
            result = remote._adapter._open_ssh_connection()
        self.assertIs(result, mock_ssh)
        mock_ssh.connect.assert_called_once_with(
            hostname="hpc-cluster.university.edu",
            port=22,
            username="hpcuser",
            password="test1234",
        )
        mock_ssh.get_transport.return_value.auth_interactive.assert_called_once()
        _, kwargs = mock_ssh.get_transport.return_value.auth_interactive.call_args
        self.assertEqual(kwargs["username"], "hpcuser")
        self.assertEqual(kwargs["submethods"], "")
        handler = kwargs["handler"]
        self.assertTrue(callable(handler))

        # The handler imports pyauthenticator lazily; stub it out since the
        # real package needs the native zbar library, which is unrelated to
        # what is being tested here (that the handler forwards the 2FA code).
        import sys
        import types

        fake_module = types.ModuleType("pyauthenticator")
        fake_module.get_two_factor_code = lambda service: "654321"
        with patch.dict(sys.modules, {"pyauthenticator": fake_module}):
            self.assertEqual(
                handler("title", "instructions", ["Verification code: "]),
                ["654321"],
            )
            self.assertEqual(handler("title", "instructions", []), [])

    def test_two_factor_without_authenticator_service(self):
        remote = _new_remote("remote_alternative")
        remote._adapter._ssh_authenticator_service = None
        with patch("pysqa.base.remote.paramiko.SSHClient") as mock_cls:
            mock_ssh = MagicMock()
            mock_cls.return_value = mock_ssh
            result = remote._adapter._open_ssh_connection()
        self.assertIs(result, mock_ssh)
        mock_ssh.get_transport.return_value.auth_interactive_dumb.assert_called_once_with(
            username="hpcuser", handler=None, submethods=""
        )

    def test_ask_for_password_with_two_factor(self):
        remote = _new_remote("remote_alternative")
        remote._adapter._ssh_password = None
        remote._adapter._ssh_authenticator_service = None
        remote._adapter._ssh_ask_for_password = True
        with (
            patch("pysqa.base.remote.paramiko.SSHClient") as mock_cls,
            patch(
                "pysqa.base.remote.getpass.getpass", return_value="typed-password"
            ) as mock_getpass,
        ):
            mock_ssh = MagicMock()
            mock_cls.return_value = mock_ssh
            result = remote._adapter._open_ssh_connection()
        self.assertIs(result, mock_ssh)
        mock_getpass.assert_called_once()
        mock_ssh.connect.assert_called_once_with(
            hostname="hpc-cluster.university.edu",
            port=22,
            username="hpcuser",
            password="typed-password",
        )
        mock_ssh.get_transport.return_value.auth_interactive_dumb.assert_called_once_with(
            username="hpcuser", handler=None, submethods=""
        )

    def test_proxy_host(self):
        remote = _new_remote("remote")
        remote._adapter._ssh_key = None
        remote._adapter._ssh_password = "test1234"
        remote._adapter._ssh_proxy_host = "proxy.example.com"
        with patch("pysqa.base.remote.paramiko.SSHClient") as mock_cls:
            mock_ssh = MagicMock()
            mock_client_new = MagicMock()
            mock_cls.side_effect = [mock_ssh, mock_client_new]
            result = remote._adapter._open_ssh_connection()
        self.assertIs(result, mock_client_new)
        self.assertIs(remote._adapter._ssh_proxy_connection, mock_ssh)
        mock_ssh.get_transport.return_value.open_channel.assert_called_once_with(
            kind="direct-tcpip",
            dest_addr=("proxy.example.com", 22),
            src_addr=("hpc-cluster.university.edu", 22),
        )
        mock_client_new.connect.assert_called_once_with(
            hostname="proxy.example.com",
            username="hpcuser",
            sock=mock_ssh.get_transport.return_value.open_channel.return_value,
        )

    def test_proxy_host_raises_value_error_without_transport(self):
        remote = _new_remote("remote")
        remote._adapter._ssh_key = None
        remote._adapter._ssh_password = "test1234"
        remote._adapter._ssh_proxy_host = "proxy.example.com"
        with patch("pysqa.base.remote.paramiko.SSHClient") as mock_cls:
            mock_ssh = MagicMock()
            mock_ssh.get_transport.return_value = None
            mock_cls.side_effect = [mock_ssh, MagicMock()]
            with self.assertRaises(ValueError):
                remote._adapter._open_ssh_connection()


@unittest.skipIf(
    skip_remote_test,
    "Either paramiko or tqdm are not installed, so the remote queue adapter tests are skipped.",
)
class TestRemoteQueueAdapterMockedHelpers(unittest.TestCase):
    """Unit tests for the remaining RemoteQueueAdapter helper methods, using
    mocks instead of a live SSH connection."""

    def test_transfer_files_raises_value_error_when_connection_is_none(self):
        remote = _new_remote("remote")
        with patch.object(remote._adapter, "_open_ssh_connection", return_value=None):
            with self.assertRaises(ValueError):
                remote._adapter._transfer_files(file_dict={"a": "b"})

    def test_execute_remote_command_returns_empty_string_when_connection_is_none(self):
        remote = _new_remote("remote")
        remote._adapter._ssh_continous_connection = False
        with patch.object(remote._adapter, "_open_ssh_connection", return_value=None):
            self.assertEqual(remote._adapter._execute_remote_command(command="pwd"), "")

    def test_create_remote_dir_with_list(self):
        remote = _new_remote("remote")
        with patch.object(remote._adapter, "_execute_remote_command") as mock_execute:
            remote._adapter._create_remote_dir(directory=["/a", "/b"])
        mock_execute.assert_called_once_with(command="mkdir -p /a /b ")

    def test_transfer_data_to_remote(self):
        remote = _new_remote("remote")
        # Use a real, non-empty directory so os.walk() actually visits files
        # and exercises the directory/file bookkeeping loop.
        local_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../../static/remote"
        )
        with (
            patch.object(remote._adapter, "_create_remote_dir") as mock_create_dir,
            patch.object(remote._adapter, "_transfer_files") as mock_transfer,
        ):
            remote._adapter._transfer_data_to_remote(working_directory=local_dir)
        mock_create_dir.assert_called_once()
        new_dir_list = mock_create_dir.call_args.kwargs["directory"]
        self.assertEqual(len(new_dir_list), 1)
        mock_transfer.assert_called_once()
        file_dict = mock_transfer.call_args.kwargs["file_dict"]
        self.assertIn(os.path.join(os.path.abspath(local_dir), "queue.yaml"), file_dict)

    def test_del_closes_open_connections(self):
        remote = _new_remote("remote")
        mock_connection = MagicMock()
        mock_proxy_connection = MagicMock()
        remote._adapter._ssh_connection = mock_connection
        remote._adapter._ssh_proxy_connection = mock_proxy_connection
        remote._adapter.__del__()
        mock_connection.close.assert_called_once()
        mock_proxy_connection.close.assert_called_once()


@unittest.skipIf(
    skip_remote_test,
    "Either paramiko or tqdm are not installed, so the remote queue adapter tests are skipped.",
)
class TestRemoteQueueAdapterPublicMethods(unittest.TestCase):
    """Unit tests for the public RemoteQueueAdapter methods, with
    _execute_remote_command mocked out so no SSH connection is required."""

    def test_submit_job(self):
        remote = _new_remote("remote")
        with patch.object(
            remote._adapter,
            "_execute_remote_command",
            return_value="Submitted batch job 42\n",
        ) as mock_execute:
            result = remote._adapter.submit_job(command="echo hello")
        self.assertEqual(result, 42)
        mock_execute.assert_called_once_with(command="echo hello")

    def test_enable_reservation(self):
        remote = _new_remote("remote")
        with patch.object(
            remote._adapter, "_execute_remote_command", return_value="ok\n"
        ) as mock_execute:
            result = remote._adapter.enable_reservation(process_id=42)
        self.assertEqual(result, "ok\n")
        mock_execute.assert_called_once_with(
            command=remote._adapter._reservation_command(job_id=42)
        )

    def test_delete_job(self):
        remote = _new_remote("remote")
        with patch.object(
            remote._adapter, "_execute_remote_command", return_value="ok\n"
        ) as mock_execute:
            result = remote._adapter.delete_job(process_id=42)
        self.assertEqual(result, "ok\n")
        mock_execute.assert_called_once_with(
            command=remote._adapter._delete_command(job_id=42)
        )

    def test_get_queue_status(self):
        remote = _new_remote("remote")
        status_json = (
            '{"jobid": [1, 2], "user": ["janj", "maxi"], "status": '
            '["running", "pending"]}'
        )
        with patch.object(
            remote._adapter, "_execute_remote_command", return_value=status_json
        ):
            df = remote._adapter.get_queue_status()
            self.assertEqual(len(df), 2)
            df_filtered = remote._adapter.get_queue_status(user="janj")
        self.assertEqual(list(df_filtered["jobid"]), [1])

    def test_get_job_from_remote_with_directories(self):
        import tempfile

        remote = _new_remote("remote")
        remote._adapter._ssh_delete_file_on_remote = True
        with tempfile.TemporaryDirectory() as local_working_directory:
            remote_working_directory = remote._adapter._get_remote_working_dir(
                working_directory=local_working_directory
            )
            with (
                patch.object(
                    remote._adapter,
                    "_execute_remote_command",
                    return_value=(
                        '{"dirs": ["'
                        + remote_working_directory
                        + '/subdir"], "files": ["out.txt"]}'
                    ),
                ) as mock_execute,
                patch.object(remote._adapter, "_transfer_files") as mock_transfer,
            ):
                remote._adapter.get_job_from_remote(
                    working_directory=local_working_directory
                )
            self.assertTrue(
                os.path.isdir(os.path.join(local_working_directory, "subdir"))
            )
            self.assertEqual(mock_transfer.call_count, 1)
            self.assertEqual(mock_execute.call_count, 2)

    def test_transfer_file(self):
        remote = _new_remote("remote")
        remote._adapter._ssh_delete_file_on_remote = True
        with (
            patch.object(remote._adapter, "_create_remote_dir") as mock_create_dir,
            patch.object(remote._adapter, "_transfer_files") as mock_transfer,
            patch.object(remote._adapter, "_execute_remote_command") as mock_execute,
        ):
            remote._adapter.transfer_file(
                file="readme.txt", transfer_back=True, delete_file_on_remote=True
            )
        mock_create_dir.assert_called_once()
        mock_transfer.assert_called_once()
        mock_execute.assert_called_once()

    def test_transfer_file_no_delete(self):
        remote = _new_remote("remote")
        remote._adapter._ssh_delete_file_on_remote = True
        with (
            patch.object(remote._adapter, "_create_remote_dir"),
            patch.object(remote._adapter, "_transfer_files"),
            patch.object(remote._adapter, "_execute_remote_command") as mock_execute,
        ):
            remote._adapter.transfer_file(file="readme.txt", transfer_back=False)
        mock_execute.assert_not_called()


@unittest.skipIf(
    skip_remote_test,
    "Either paramiko or tqdm are not installed, so the remote queue adapter tests are skipped.",
)
class TestTransferFilesSftp(unittest.TestCase):
    """Unit tests for the SFTP transfer loop in _transfer_files(), with the
    SSH connection mocked out."""

    def test_transfer_files_put(self):
        remote = _new_remote("remote")
        remote._adapter._ssh_continous_connection = False
        mock_sftp = MagicMock()
        mock_ssh = MagicMock()
        mock_ssh.open_sftp.return_value = mock_sftp
        with patch.object(
            remote._adapter, "_open_ssh_connection", return_value=mock_ssh
        ):
            remote._adapter._transfer_files(
                file_dict={"local.txt": "remote.txt"}, transfer_back=False
            )
        mock_sftp.put.assert_called_once_with("local.txt", "remote.txt")
        mock_sftp.close.assert_called_once()

    def test_transfer_files_get_existing_file(self):
        remote = _new_remote("remote")
        remote._adapter._ssh_continous_connection = False
        mock_sftp = MagicMock()
        mock_ssh = MagicMock()
        mock_ssh.open_sftp.return_value = mock_sftp
        with patch.object(
            remote._adapter, "_open_ssh_connection", return_value=mock_ssh
        ):
            remote._adapter._transfer_files(
                file_dict={"local.txt": "remote.txt"}, transfer_back=True
            )
        mock_sftp.stat.assert_called_once_with("remote.txt")
        mock_sftp.get.assert_called_once_with("remote.txt", "local.txt")

    def test_transfer_files_get_missing_file_is_ignored(self):
        remote = _new_remote("remote")
        remote._adapter._ssh_continous_connection = False
        mock_sftp = MagicMock()
        mock_sftp.stat.side_effect = FileNotFoundError
        mock_ssh = MagicMock()
        mock_ssh.open_sftp.return_value = mock_sftp
        with patch.object(
            remote._adapter, "_open_ssh_connection", return_value=mock_ssh
        ):
            remote._adapter._transfer_files(
                file_dict={"local.txt": "remote.txt"}, transfer_back=True
            )
        mock_sftp.get.assert_not_called()

    def test_transfer_files_with_provided_sftp_does_not_open_connection(self):
        remote = _new_remote("remote")
        mock_sftp = MagicMock()
        with patch.object(remote._adapter, "_open_ssh_connection") as mock_open:
            remote._adapter._transfer_files(
                file_dict={"local.txt": "remote.txt"},
                sftp=mock_sftp,
                transfer_back=False,
            )
        mock_open.assert_not_called()
        mock_sftp.put.assert_called_once_with("local.txt", "remote.txt")
        mock_sftp.close.assert_not_called()

    def test_transfer_files_continuous_connection(self):
        remote = _new_remote("remote")
        remote._adapter._ssh_continous_connection = True
        mock_sftp = MagicMock()
        mock_ssh = MagicMock()
        mock_ssh.open_sftp.return_value = mock_sftp
        with patch.object(
            remote._adapter, "_open_ssh_connection", return_value=mock_ssh
        ) as mock_open:
            remote._adapter._transfer_files(
                file_dict={"local.txt": "remote.txt"}, transfer_back=False
            )
        mock_open.assert_called_once()
        self.assertIs(remote._adapter._ssh_connection, mock_ssh)
