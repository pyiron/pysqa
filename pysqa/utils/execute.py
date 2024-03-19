import os
import subprocess
from typing import Optional


def execute_command(
    commands: str,
    working_directory: Optional[str] = None,
    split_output: bool = True,
    shell: bool = False,
    error_filename: str = "pysqa.err",
) -> str:
    """
    A wrapper around the subprocess.check_output function.

    Args:
        commands (list/str): These commands are executed on the command line
        working_directory (str/None): The directory where the command is executed
        split_output (bool): Boolean flag to split newlines in the output
        shell (bool): Additional switch to convert list of commands to one string
        error_filename (str): In case the execution fails the output is written to this file

    Returns:
        str/list: output of the shell command either as string or as a list of strings
    """
    if shell and isinstance(commands, list):
        commands = " ".join(commands)
    try:
        out = subprocess.check_output(
            commands,
            cwd=working_directory,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=not isinstance(commands, list),
        )
    except subprocess.CalledProcessError as e:
        with open(os.path.join(working_directory, error_filename), "w") as f:
            print(e.stdout, file=f)
        out = None
    if out is not None and split_output:
        return out.split("\n")
    else:
        return out
