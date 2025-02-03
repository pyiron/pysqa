import os
from typing import Optional, Union

import pandas
from jinja2 import Template

from pysqa.wrapper.abstract import SchedulerCommands

template = """\
#!/bin/bash
#SBATCH --output=time.out
#SBATCH --job-name={{job_name}}
#SBATCH --chdir={{working_directory}}
#SBATCH --get-user-env=L
#SBATCH --partition={{partition}}
{%- if run_time_max %}
#SBATCH --time={{ [1, run_time_max // 60]|max }}
{%- endif %}
{%- if dependency %}
#SBATCH --dependency=afterok:{{ dependency | join(',') }}
{%- endif %}
{%- if memory_max %}
#SBATCH --mem={{memory_max}}G
{%- endif %}
#SBATCH --cpus-per-task={{cores}}

{{command}}
"""


class SlurmCommands(SchedulerCommands):
    @property
    def submit_job_command(self) -> list[str]:
        """Returns the command to submit a job to Slurm."""
        return ["sbatch", "--parsable"]

    @property
    def delete_job_command(self) -> list[str]:
        """Returns the command to delete a job from Slurm."""
        return ["scancel"]

    @property
    def get_queue_status_command(self) -> list[str]:
        """Returns the command to get the queue status from Slurm."""
        return ["squeue", "--format", "%A|%u|%t|%.15j|%Z", "--noheader"]

    @staticmethod
    def get_job_id_from_output(queue_submit_output: str) -> int:
        """Extracts the job ID from the output of the job submission command."""
        return int(queue_submit_output.splitlines()[-1].rstrip().lstrip().split()[-1])

    @staticmethod
    def convert_queue_status(queue_status_output: str) -> pandas.DataFrame:
        """Converts the queue status output from Slurm into a pandas DataFrame."""
        line_split_lst = [line.split("|") for line in queue_status_output.splitlines()]
        if len(line_split_lst) != 0:
            job_id_lst, user_lst, status_lst, job_name_lst, working_directory_lst = zip(
                *[
                    (int(jobid), user, status.lower(), jobname, working_directory)
                    for jobid, user, status, jobname, working_directory in line_split_lst
                ]
            )
        else:
            job_id_lst, user_lst, status_lst, job_name_lst, working_directory_lst = (
                [],
                [],
                [],
                [],
                [],
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
        df.loc[df.status == "r", "status"] = "running"
        df.loc[df.status == "pd", "status"] = "pending"
        return df

    @staticmethod
    def dependencies(dependency_list: list[str]) -> list[str]:
        """Returns the dependency options for job submission."""
        if dependency_list is not None:
            return ["--dependency=afterok:" + ",".join(dependency_list)]
        else:
            return []

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
