import os
import unittest
from pysqa.utils.execute import execute_command


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
