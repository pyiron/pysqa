import os
from typing import Optional, Union

import pandas
from jinja2 import Template

from pysqa.wrapper.abstract import SchedulerCommands

template = """\
#!/bin/bash
#BSUB -q queue
#BSUB -J {{job_name}}
#BSUB -o time.out
#BSUB -n {{cores}}
#BSUB -cwd {{working_directory}}
#BSUB -e error.out
{%- if run_time_max %}
#BSUB -W {{run_time_max}}
{%- endif %}
{%- if memory_max %}
#BSUB -M {{memory_max}}
{%- endif %}

{{command}}
"""


class LsfCommands(SchedulerCommands):
    @property
    def submit_job_command(self) -> list[str]:
        """Return the command to submit a job."""
        return ["bsub"]

    @property
    def delete_job_command(self) -> list[str]:
        """Return the command to delete a job."""
        return ["bkill"]

    @property
    def get_queue_status_command(self) -> list[str]:
        """Return the command to get the queue status."""
        return ["bjobs"]

    @staticmethod
    def get_job_id_from_output(queue_submit_output: str) -> int:
        """Extract the job ID from the queue submit output."""
        return int(queue_submit_output.split("<")[1].split(">")[0])

    @staticmethod
    def convert_queue_status(queue_status_output: str) -> pandas.DataFrame:
        """Convert the queue status output to a pandas DataFrame."""
        job_id_lst, user_lst, status_lst, job_name_lst = [], [], [], []
        line_split_lst = queue_status_output.split("\n")
        if len(line_split_lst) > 1:
            for line in line_split_lst[1:]:
                line_segments = line.split()
                if len(line_segments) > 1:
                    job_id_lst.append(int(line_segments[0]))
                    user_lst.append(line_segments[1])
                    status_lst.append(line_segments[2])
                    job_name_lst.append(line_segments[6])
        df = pandas.DataFrame(
            {
                "jobid": job_id_lst,
                "user": user_lst,
                "jobname": job_name_lst,
                "status": status_lst,
            }
        )
        df.loc[df.status == "RUN", "status"] = "running"
        df.loc[df.status == "PEND", "status"] = "pending"
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
