import os
import unittest
from pysqa import QueueAdapter

try:
    import paramiko
    from tqdm import tqdm
    from pysqa.base.remote import get_transport

    skip_remote_test = False
except ImportError:
    skip_remote_test = True


@unittest.skipIf(
    skip_remote_test,
    "Either paramiko or tqdm are not installed, so the remote queue adapter tests are skipped.",
)
class TestRemoteQueueAdapterAuth(unittest.TestCase):
    def test_password_auth(self):
        path = os.path.dirname(os.path.abspath(__file__))
        remote = QueueAdapter(directory=os.path.join(path, "config/remote_rebex_hosts"))
        remote._adapter._ssh_ask_for_password = False
        remote._adapter._ssh_key = None
        self.assertIsNotNone(remote._adapter._open_ssh_connection())

    def test_key_auth(self):
        path = os.path.dirname(os.path.abspath(__file__))
        remote = QueueAdapter(directory=os.path.join(path, "config/remote_rebex_hosts"))
        remote._adapter._ssh_password = None
        with self.assertRaises(ValueError):
            remote._adapter._open_ssh_connection()

    def test_two_factor_auth(self):
        path = os.path.dirname(os.path.abspath(__file__))
        remote = QueueAdapter(directory=os.path.join(path, "config/remote_rebex_hosts"))
        remote._adapter._ssh_two_factor_authentication = True
        with self.assertRaises(paramiko.ssh_exception.AuthenticationException):
            remote._adapter._open_ssh_connection()
