# coding: utf-8
import pandas
from flux.job import JobID

from pysqa.wrapper.generic import SchedulerCommands


class FluxCommands(SchedulerCommands):
    @property
    def submit_job_command(self) -> list[str]:
        return ["flux", "batch"]

    @property
    def delete_job_command(self) -> list[str]:
        return ["flux", "cancel"]

    @property
    def get_queue_status_command(self) -> list[str]:
        return ["flux", "jobs", "-a", "--no-header"]

    @staticmethod
    def get_job_id_from_output(queue_submit_output: str) -> int:
        return int(
            JobID(queue_submit_output.splitlines()[-1].rstrip().lstrip().split()[-1])
        )

    @staticmethod
    def convert_queue_status(queue_status_output: str) -> pandas.DataFrame:
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
