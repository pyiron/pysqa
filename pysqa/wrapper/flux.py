import os
from typing import Optional, Union

import pandas
from flux.job import JobID
from jinja2 import Template

from pysqa.wrapper.abstract import SchedulerCommands

template = """\
#!/bin/bash
# flux: --job-name={{job_name}}
# flux: --env=CORES={{cores}}
# flux: --output=time.out
# flux: --error=error.out
# flux: -n {{cores}}
{%- if run_time_max %}
# flux: -t {{ [1, run_time_max // 60]|max }}
{%- endif %}
{%- if dependency %}
{%- for jobid in dependency %}
# flux: --dependency=afterok:{{jobid}}
{%- endfor %}
{%- endif %}

{{command}}
"""


class FluxCommands(SchedulerCommands):
    @property
    def submit_job_command(self) -> list[str]:
        """Returns the command to submit a job."""
        return ["flux", "batch"]

    @property
    def delete_job_command(self) -> list[str]:
        """Returns the command to delete a job."""
        return ["flux", "cancel"]

    @property
    def get_queue_status_command(self) -> list[str]:
        """Returns the command to get the queue status."""
        return ["flux", "jobs", "-a", "--no-header"]

    @staticmethod
    def get_job_id_from_output(queue_submit_output: str) -> int:
        """Extracts the job ID from the output of the queue submit command."""
        return int(
            JobID(queue_submit_output.splitlines()[-1].rstrip().lstrip().split()[-1])
        )

    @staticmethod
    def convert_queue_status(queue_status_output: str) -> pandas.DataFrame:
        """Converts the queue status output into a pandas DataFrame."""
        line_split_lst = [line.split() for line in queue_status_output.splitlines()]
        job_id_lst, user_lst, job_name_lst, status_lst = [], [], [], []
        for entry in line_split_lst:
            job_id_lst.append(JobID(entry[0]))
            user_lst.append(entry[1])
            job_name_lst.append(entry[2])
            status_lst.append(entry[3])
        df = pandas.DataFrame(
            {
                "jobid": job_id_lst,
                "user": user_lst,
                "jobname": job_name_lst,
                "status": status_lst,
            }
        )
        df.loc[df.status == "R", "status"] = "running"
        df.loc[df.status == "S", "status"] = "pending"
        df.loc[df.status == "C", "status"] = "error"
        df.loc[df.status == "CD", "status"] = "finished"
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
