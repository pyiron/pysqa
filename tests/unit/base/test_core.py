import os
import unittest
from pysqa.base.core import QueueAdapterCore, execute_command


class TestExecuteCommand(unittest.TestCase):
    def test_commands_as_lst(self):
        output = execute_command(
            commands=["echo", "hello"],
            working_directory=".",
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        )
        self.assertEqual(output, ["hello", ""])

    def test_commands_as_lst_no_split(self):
        output = execute_command(
            commands=["echo", "hello"],
            working_directory=".",
            split_output=False,
            shell=False,
            error_filename="pysqa.err",
        )
        self.assertEqual(output, "hello\n")

    def test_commands_as_lst_shell_true(self):
        output = execute_command(
            commands=["echo", "hello"],
            working_directory=".",
            split_output=True,
            shell=True,
            error_filename="pysqa.err",
        )
        self.assertEqual(output, ["hello", ""])

    def test_commands_as_str(self):
        output = execute_command(
            commands="echo hello",
            working_directory=".",
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        )
        self.assertEqual(output, ["hello", ""])

    def test_commands_fails(self):
        output = execute_command(
            commands="exit 1",
            working_directory=".",
            split_output=True,
            shell=False,
            error_filename="pysqa_fails.err",
        )
        self.assertIsNone(output)
        with open("pysqa_fails.err") as f:
            error = f.readlines()
        self.assertEqual(error, ["\n"])
        os.remove("pysqa_fails.err")

    def test_commands_fails_no_working_directory(self):
        output = execute_command(
            commands="exit 1",
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa_fails.err",
        )
        self.assertIsNone(output)
        with open("pysqa_fails.err") as f:
            error = f.readlines()
        self.assertEqual(error, ["\n"])
        os.remove("pysqa_fails.err")


class TestQueueAdapterCore(unittest.TestCase):
    def test_job_submission_template_named_queue_raises_value_error(self):
        qa = QueueAdapterCore(queue_type="SLURM")
        with self.assertRaises(ValueError) as context:
            qa._job_submission_template(queue="some_queue")
        self.assertIn("some_queue", str(context.exception))

    def test_write_queue_script_command_as_list(self):
        qa = QueueAdapterCore(queue_type="SLURM")
        working_directory, queue_script_path = qa._write_queue_script(
            command=["echo ", "hello"]
        )
        with open(queue_script_path) as f:
            content = f.read()
        self.assertTrue(content.endswith("echo hello"))
        os.remove(queue_script_path)

    def test_no_commands_for_remote_queue_type(self):
        # The "REMOTE" queue type has no associated scheduler commands class,
        # so QueueAdapterCore falls back to its no-op/None branches.
        qa = QueueAdapterCore(queue_type="REMOTE")
        self.assertIsNone(qa._commands)
        self.assertIsNone(qa.enable_reservation(process_id=1))
        self.assertIsNone(qa.delete_job(process_id=1))
        self.assertIsNone(qa.get_queue_status())
        self.assertEqual(qa._list_command_to_be_executed(queue_script_path="x"), [])
        self.assertEqual(qa._job_submission_template(command="echo hello"), "")
