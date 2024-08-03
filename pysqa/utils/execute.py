import os
import subprocess
from typing import Optional, Union, List


def execute_command(
    commands: str,
    working_directory: Optional[str] = None,
    split_output: bool = True,
    shell: bool = False,
    error_filename: str = "pysqa.err",
) -> Union[str, List[str]]:
    """
    A wrapper around the subprocess.check_output function.

    Args:
        commands (str): The command(s) to be executed on the command line
        working_directory (str, optional): The directory where the command is executed. Defaults to None.
        split_output (bool, optional): Boolean flag to split newlines in the output. Defaults to True.
        shell (bool, optional): Additional switch to convert commands to a single string. Defaults to False.
        error_filename (str, optional): In case the execution fails, the output is written to this file. Defaults to "pysqa.err".

    Returns:
        Union[str, List[str]]: Output of the shell command either as a string or as a list of strings
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
