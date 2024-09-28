import pandas

from pysqa.wrapper.generic import SchedulerCommands


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
