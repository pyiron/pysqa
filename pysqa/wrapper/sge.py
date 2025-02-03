import os
from typing import Optional, Union

import defusedxml.ElementTree as ETree
import pandas
from jinja2 import Template

from pysqa.wrapper.abstract import SchedulerCommands

template = """\
#!/bin/bash
#$ -N {{job_name}}
#$ -wd {{working_directory}}
{%- if cores %}
#$ -pe {{partition}} {{cores}}
{%- endif %}
{%- if memory_max %}
#$ -l h_vmem={{memory_max}}
{%- endif %}
{%- if run_time_max %}
#$ -l h_rt={{run_time_max}}
{%- endif %}
#$ -o time.out
#$ -e error.out

{{command}}
"""


class SunGridEngineCommands(SchedulerCommands):
    @property
    def submit_job_command(self) -> list[str]:
        """Return the command to submit a job."""
        return ["qsub", "-terse"]

    @property
    def delete_job_command(self) -> list[str]:
        """Return the command to delete a job."""
        return ["qdel"]

    @property
    def enable_reservation_command(self) -> list[str]:
        """Return the command to enable job reservation."""
        return ["qalter", "-R", "y"]

    @property
    def get_queue_status_command(self) -> list[str]:
        """Return the command to get the queue status."""
        return ["qstat", "-xml"]

    @staticmethod
    def convert_queue_status(queue_status_output: str) -> pandas.DataFrame:
        """Convert the queue status output to a pandas DataFrame.

        Args:
            queue_status_output: The output of the queue status command.

        Returns:
            A pandas DataFrame containing the converted queue status.

        """

        def leaf_to_dict(leaf):
            return [
                {sub_child.tag: sub_child.text for sub_child in child} for child in leaf
            ]

        tree = ETree.fromstring(queue_status_output)
        df_running_jobs = pandas.DataFrame(leaf_to_dict(leaf=tree[0]))
        df_pending_jobs = pandas.DataFrame(leaf_to_dict(leaf=tree[1]))
        df_merge = pandas.concat([df_running_jobs, df_pending_jobs], sort=True)
        df_merge.loc[df_merge.state == "r", "state"] = "running"
        df_merge.loc[df_merge.state == "qw", "state"] = "pending"
        df_merge.loc[df_merge.state == "Eqw", "state"] = "error"
        return pandas.DataFrame(
            {
                "jobid": pandas.to_numeric(df_merge.JB_job_number),
                "user": df_merge.JB_owner,
                "jobname": df_merge.JB_name,
                "status": df_merge.state,
                "working_directory": [""] * len(df_merge),
            }
        )

    @staticmethod
    def get_job_id_from_output(queue_submit_output: str) -> int:
        """Extracts the job ID from the output of the job submission command."""
        return int(queue_submit_output.strip().split(".")[0])

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
