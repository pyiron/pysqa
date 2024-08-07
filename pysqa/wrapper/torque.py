# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import re

import pandas

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
