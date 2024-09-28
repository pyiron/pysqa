# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import os
from typing import List, Optional, Union

from jinja2 import Template

from pysqa.wrapper.generic import SchedulerCommands

__author__ = "Jan Janssen"
__copyright__ = (
    "Copyright 2019, Max-Planck-Institut für Eisenforschung GmbH - "
    "Computational Materials Design (CM) Department"
)
__version__ = "1.0"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "development"
__date__ = "Feb 9, 2019"


template = """\
#!/bin/bash
#MSUB -N {{job_name}}
{%- if memory_max %}
#MSUB -l pmem={{ memory_max| int }}gb
{%- endif %}
{%- if run_time_max %}
#$ -l walltime={{run_time_max}}
{%- endif %}

{{command}}
"""


class MoabCommands(SchedulerCommands):
    @property
    def submit_job_command(self) -> list[str]:
        """
        Get the command to submit a job.

        Returns:
            list[str]: The command to submit a job.
        """
        return ["msub"]

    @property
    def delete_job_command(self) -> list[str]:
        """
        Get the command to delete a job.

        Returns:
            list[str]: The command to delete a job.
        """
        return ["mjobctl", "-c"]

    @property
    def get_queue_status_command(self) -> list[str]:
        """
        Get the command to get the queue status.

        Returns:
            list[str]: The command to get the queue status.
        """
        return ["mdiag", "-x"]

    @staticmethod
    def render_submission_template(
        command: str,
        job_name: str = "pysqa",
        working_directory: str = os.path.abspath("."),
        cores: int = 1,
        memory_max: Optional[int] = None,
        run_time_max: Optional[int] = None,
        dependency_list: Optional[List[int]] = None,
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
            submission_template (str): Submission script template pysqa.wrapper.torque.template

        Returns:
            str: The rendered job submission template.
        """
        if isinstance(submission_template, Template):
            submission_template = Template(submission_template)
        return submission_template.render(
            command=command,
            job_name=job_name,
            working_directory=working_directory,
            cores=cores,
            memory_max=memory_max,
            run_time_max=run_time_max,
            dependency_list=dependency_list,
            **kwargs,
        )
