from typing import Union

import pandas

from pysqa.wrapper.slurm import SlurmCommands
from pysqa.wrapper.slurm import template as template_slurm

template = template_slurm


class GentCommands(SlurmCommands):
    @staticmethod
    def get_job_id_from_output(queue_submit_output: str) -> int:
        """
        Extracts the job ID from the queue submit output.

        Args:
            queue_submit_output (str): The output of the queue submit command.

        Returns:
            int: The job ID.

        """
        return int(queue_submit_output.splitlines()[-1].rstrip().lstrip().split(";")[0])

    @staticmethod
    def get_queue_from_output(queue_submit_output: str) -> str:
        """
        Extracts the queue name from the queue submit output.

        Args:
            queue_submit_output (str): The output of the queue submit command.

        Returns:
            str: The queue name.

        """
        return str(queue_submit_output.splitlines()[-1].rstrip().lstrip().split(";")[1])

    @staticmethod
    def convert_queue_status(queue_status_output: str) -> Union[pandas.DataFrame, None]:
        """
        Converts the queue status output into a pandas DataFrame.

        Args:
            queue_status_output (str): The output of the queue status command.

        Returns:
            pandas.DataFrame: The converted queue status.

        """
        qstat = queue_status_output.splitlines()
        queue = qstat[0].split(":")[1].strip()
        if len(qstat) <= 1:  # first row contains cluster name, check if there are jobs
            return None

        line_split_lst = [line.split("|") for line in qstat[1:]]
        job_id_lst, user_lst, status_lst, job_name_lst, queue_lst = zip(
            *[
                (int(jobid), user, status.lower(), jobname, queue)
                for jobid, user, status, jobname in line_split_lst
            ]
        )
        return pandas.DataFrame(
            {
                "cluster": queue_lst,
                "jobid": job_id_lst,
                "user": user_lst,
                "jobname": job_name_lst,
                "status": status_lst,
            }
        )

    @staticmethod
    def dependencies(dependency_list: list[str]) -> list[str]:
        """
        Returns the dependencies for the job.

        Args:
            dependency_list (list[str]): The list of job dependencies.

        Returns:
            list[str]: The dependencies for the job.

        Raises:
            NotImplementedError: If dependency_list is not None.

        """
        if dependency_list is not None:
            raise NotImplementedError()
        else:
            return []
