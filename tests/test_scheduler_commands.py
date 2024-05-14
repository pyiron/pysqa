import unittest
from pysqa.wrapper.generic import SchedulerCommands


class TmpSchedularCommands(SchedulerCommands):
    def delete_job_command(self):
        pass

    def get_queue_status_command(self):
        pass

    def submit_job_command(self):
        pass


class TestSchedulerCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.commands = TmpSchedularCommands()

    def test_enable_reservation_command(self):
        with self.assertRaises(NotImplementedError):
            self.commands.enable_reservation_command()

    def test_get_job_id_from_output(self):
        with self.assertRaises(NotImplementedError):
            self.commands.get_job_id_from_output("test")

    def test_convert_queue_status(self):
        with self.assertRaises(NotImplementedError):
            self.commands.convert_queue_status("test")

    def test_no_delete_job_command(self):
        class NoDelteteSchedularCommands(SchedulerCommands):
            def get_queue_status_command(self):
                pass

            def submit_job_command(self):
                pass

        with self.assertRaises(TypeError):
            NoDelteteSchedularCommands()

    def test_get_queue_status_command(self):
        class NoQueueStatusSchedularCommands(SchedulerCommands):
            def delete_job_command(self):
                pass

            def submit_job_command(self):
                pass

        with self.assertRaises(TypeError):
            NoQueueStatusSchedularCommands()

    def test_submit_job_command(self):
        class NoSubmitSchedularCommands(SchedulerCommands):
            def delete_job_command(self):
                pass

            def get_queue_status_command(self):
                pass

        with self.assertRaises(TypeError):
            NoSubmitSchedularCommands()
