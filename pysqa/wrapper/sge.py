import defusedxml.ElementTree as ETree
import pandas

from pysqa.wrapper.generic import SchedulerCommands


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
