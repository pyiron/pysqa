# coding: utf-8
from flux.job import JobID
import pandas
from pysqa.wrapper.generic import SchedulerCommands


class FluxCommands(SchedulerCommands):
    @property
    def submit_job_command(self):
        return ["flux", "batch"]

    @property
    def delete_job_command(self):
        return ["flux", "cancel"]

    @property
    def get_queue_status_command(self):
        return ["flux", "jobs", "-a", "--no-header"]

    @staticmethod
    def get_job_id_from_output(queue_submit_output):
        return JobID(queue_submit_output.splitlines()[-1].rstrip().lstrip().split()[-1])

    @staticmethod
    def convert_queue_status(queue_status_output):
        line_split_lst = [line.split() for line in queue_status_output.splitlines()]
        job_id_lst, user_lst, job_name_lst, status_lst = [], [], [], []
        for (
            flux_id,
            user,
            job_name,
            status,
            task,
            nodes,
            runtime,
            ranks,
        ) in line_split_lst:
            job_id_lst.append(JobID(flux_id))
            user_lst.append(user)
            job_name_lst.append(job_name)
            status_lst.append(status)
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
        return df
