import os
import re
from typing import Optional, Union

import pandas
from jinja2 import Template

from pysqa.wrapper.abstract import SchedulerCommands

template = """\
#!/bin/bash
#PBS -l ncpus={{cores}}
#PBS -N {{job_name}}
{%- if memory_max %}
#PBS -l mem={{ memory_max| int }}GB
{%- endif %}
{%- if run_time_max %}
#PBS -l walltime={{run_time_max}} 
{%- endif %}
#PBS -l wd
{%- if dependency %}
#PBS -W depend=afterok:{{ dependency | join(':') }}
{%- endif %}
 
{{command}}
"""


class TorqueCommands(SchedulerCommands):
    @property
    def submit_job_command(self) -> list[str]:
        """Returns the command to submit a job."""
        return ["qsub"]

    @property
    def delete_job_command(self) -> list[str]:
        """Returns the command to delete a job."""
        return ["qdel"]

    @property
    def get_queue_status_command(self) -> list[str]:
        """Returns the command to get the queue status."""
        return ["qstat", "-f"]

    @staticmethod
    def get_job_id_from_output(queue_submit_output: str) -> int:
        """Extracts the job ID from the queue submit output.

        Args:
            queue_submit_output (str): The output of the queue submit command.

        Returns:
            int: The job ID.

        Raises:
            ValueError: If the job ID cannot be extracted.
        """
        return int(
            queue_submit_output.splitlines()[-1].rstrip().lstrip().split(sep=".")[0]
        )

    @staticmethod
    def convert_queue_status(queue_status_output: str) -> pandas.DataFrame:
        """Converts the queue status output into a pandas DataFrame.

        Args:
            queue_status_output (str): The output of the queue status command.

        Returns:
            pandas.DataFrame: The queue status as a DataFrame.
        """
        lines = queue_status_output.split("\n")
        input_string = "".join(lines)
        # remove all whitespaces
        input_string = "".join(input_string.split())

        # Extract the job ID, user, job name, status, and working directory for each running job
        regex_pattern_job_id = r"JobId:(.*?)Job_Name"
        job_id_lst = re.findall(regex_pattern_job_id, input_string)
        job_id_lst = [int(job_id_str.split(sep=".")[0]) for job_id_str in job_id_lst]

        regex_pattern_user = r"Job_Owner=(.*?)job_state"
        user_lst = re.findall(regex_pattern_user, input_string)
        user_lst = [user_str.split("@")[0] for user_str in user_lst]

        regex_pattern_job_name = r"Job_Name=(.*?)Job_Owner"
        job_name_lst = re.findall(regex_pattern_job_name, input_string)

        regex_pattern_status = r"job_state=(.*?)queue"
        status_lst = re.findall(regex_pattern_status, input_string)

        regex_pattern_working_directory = r"PBS_O_WORKDIR=(.*?),PBS"
        working_directory_lst = re.findall(
            regex_pattern_working_directory, input_string
        )

        df = pandas.DataFrame(
            {
                "jobid": job_id_lst,
                "user": user_lst,
                "jobname": job_name_lst,
                "status": status_lst,
                "working_directory": working_directory_lst,
            }
        )

        df["status"] = df["status"].apply(
            lambda x: "running" if x == "R" else "pending"
        )

        return df

    def render_submission_template(
        self,
        command: str,
        job_name: str = "pysqa",
        working_directory: str = os.path.abspath("."),
        cores: int = 1,
        memory_max: Optional[int] = None,
        run_time_max: Optional[int] = None,
        dependency_list: Optional[list[int]] = None,
        submission_template: Union[str, Template] = template,
        **kwargs,
    ) -> str:
        """
        Generate the job submission template.

        Args:
            command (str, optional): The command to be executed.
            job_name (str, optional): The job name. Defaults to "pysqa".
            working_directory (str, optional): The working directory. Defaults to ".".
            cores (int, optional): The number of cores. Defaults to 1.
            memory_max (int, optional): The maximum memory. Defaults to None.
            run_time_max (int, optional): The maximum run time. Defaults to None.
            dependency_list (list[int], optional): The list of dependency job IDs. Defaults to None.
            submission_template (str): Submission script template pysqa.wrapper.flux.template

        Returns:
            str: The rendered job submission template.
        """
        return super().render_submission_template(
            command=command,
            job_name=job_name,
            working_directory=working_directory,
            cores=cores,
            memory_max=memory_max,
            run_time_max=run_time_max,
            dependency_list=dependency_list,
            submission_template=submission_template,
            **kwargs,
        )
