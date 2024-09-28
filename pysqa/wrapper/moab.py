from pysqa.wrapper.generic import SchedulerCommands


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
