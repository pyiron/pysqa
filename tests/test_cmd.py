import os
import io
import json
import unittest
import unittest.mock
from pysqa.cmd import command_line


class TestCMD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.abspath(os.path.dirname(__file__))

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def assert_stdout_command_line(
        self, cmd_args, execute_command, expected_output, mock_stdout
    ):
        command_line(arguments_lst=cmd_args, execute_command=execute_command)
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    def test_help(self):
        self.assert_stdout_command_line(
            ["--help"],
            None,
            "python -m pysqa --help ... coming soon.\n",
        )

    def test_wrong_option(self):
        self.assert_stdout_command_line(
            ["--error"],
            None,
            "python -m pysqa --help\n",
        )

    def test_submit(self):
        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            return "1\n"

        self.assert_stdout_command_line(
            [
                "--config_directory",
                os.path.join(self.test_dir, "config", "slurm"),
                "--submit",
                "--queue",
                "slurm",
                "--job_name",
                "test",
                "--working_directory",
                ".",
                "--cores",
                "2",
                "--memory",
                "1GB",
                "--run_time",
                "10",
                "--command",
                "echo hello",
            ],
            execute_command,
            "1\n",
        )
        with open("run_queue.sh") as f:
            output = f.readlines()
        content = [
            "#!/bin/bash\n",
            "#SBATCH --output=time.out\n",
            "#SBATCH --job-name=test\n",
            "#SBATCH --chdir=.\n",
            "#SBATCH --get-user-env=L\n",
            "#SBATCH --partition=slurm\n",
            "#SBATCH --time=4320\n",
            "#SBATCH --mem=1GBG\n",
            "#SBATCH --cpus-per-task=10\n",
            "\n",
            "echo hello",
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

        self.assert_stdout_command_line(
            [
                "--config_directory",
                os.path.join(self.test_dir, "config", "slurm"),
                "--delete",
                "--id",
                "1",
            ],
            execute_command,
            "S\n",
        )

    def test_status(self):
        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            with open(
                os.path.join(self.test_dir, "config", "slurm", "squeue_output")
            ) as f:
                return f.read()

        self.assert_stdout_command_line(
            [
                "--config_directory",
                os.path.join(self.test_dir, "config", "slurm"),
                "--status",
            ],
            execute_command,
            json.dumps(
                {
                    "jobid": [5322019, 5322016, 5322017, 5322018, 5322013],
                    "user": ["janj", "janj", "janj", "janj", "maxi"],
                    "jobname": [
                        "pi_19576488",
                        "pi_19576485",
                        "pi_19576486",
                        "pi_19576487",
                        "pi_19576482",
                    ],
                    "status": ["running", "running", "running", "running", "running"],
                    "working_directory": [
                        "/cmmc/u/janj/pyiron/projects/2023/2023-04-19-dft-test/job_1",
                        "/cmmc/u/janj/pyiron/projects/2023/2023-04-19-dft-test/job_2",
                        "/cmmc/u/janj/pyiron/projects/2023/2023-04-19-dft-test/job_3",
                        "/cmmc/u/janj/pyiron/projects/2023/2023-04-19-dft-test/job_4",
                        "/cmmc/u/janj/pyiron/projects/2023/2023-04-19-dft-test/job_5",
                    ],
                }
            )
            + "\n",
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

        self.assert_stdout_command_line(
            [
                "--config_directory",
                os.path.join(self.test_dir, "config", "slurm"),
                "--list",
                "--working_directory",
                os.path.join(self.test_dir, "config", "slurm"),
            ],
            execute_command,
            json.dumps(
                {
                    "dirs": [os.path.join(self.test_dir, "config", "slurm")],
                    "files": sorted(
                        [
                            os.path.join(
                                self.test_dir, "config", "slurm", "squeue_output"
                            ),
                            os.path.join(
                                self.test_dir, "config", "slurm", "slurm_extra.sh"
                            ),
                            os.path.join(self.test_dir, "config", "slurm", "slurm.sh"),
                            os.path.join(
                                self.test_dir, "config", "slurm", "queue.yaml"
                            ),
                        ]
                    ),
                }
            )
            + "\n",
        )
