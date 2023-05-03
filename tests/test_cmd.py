import os
import unittest
from pysqa.cmd import command_line


class TestCMD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.abspath(os.path.dirname(__file__))

    def test_help(self):
        with self.assertRaises(SystemExit):
            command_line(["--help"])

    def test_wrong_option(self):
        with self.assertRaises(SystemExit):
            command_line(["--error"])

    def test_submit(self):
        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            return "1\n"

        with self.assertRaises(SystemExit):
            command_line(
                [
                    "--config_directory", os.path.join(self.test_dir, "config", "slurm"),
                    "--submit",
                    "--queue", "slurm",
                    "--job_name", "test",
                    "--working_directory", ".",
                    "--cores", "2",
                    "--memory", "1GB",
                    "--run_time", "10",
                    "--command", "echo hello"
                ],
                execute_command=execute_command
            )
        with open("run_queue.sh") as f:
            output = f.readlines()
        content = [
            '#!/bin/bash\n',
            '#SBATCH --output=time.out\n',
            '#SBATCH --job-name=test\n',
            '#SBATCH --chdir=.\n',
            '#SBATCH --get-user-env=L\n',
            '#SBATCH --partition=slurm\n',
            '#SBATCH --time=4320\n',
            '#SBATCH --mem=1GBG\n',
            '#SBATCH --cpus-per-task=10\n',
            '\n',
            'echo hello'
        ]
        self.assertEqual(output, content)
        os.remove("run_queue.sh")

    def test_delete(self):
        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            return "Success\n"

        with self.assertRaises(SystemExit):
            command_line(
                [
                    "--config_directory", os.path.join(self.test_dir, "config", "slurm"),
                    "--delete",
                    "--id", "1",
                ],
                execute_command=execute_command
            )

    def test_status(self):

        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            with open(os.path.join(self.test_dir, "config", "slurm", "squeue_output")) as f:
                return f.read()

        with self.assertRaises(SystemExit):
            command_line(
                [
                    "--config_directory", os.path.join(self.test_dir, "config", "slurm"),
                    "--status"
                ],
                execute_command=execute_command
            )

    def test_list(self):
        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            pass

        with self.assertRaises(SystemExit):
            command_line(
                [
                    "--config_directory", os.path.join(self.test_dir, "config", "slurm"),
                    "--list",
                    "--working_directory", os.path.join(self.test_dir, "config", "slurm"),

                ],
                execute_command=execute_command
            )
