import os

import pandas
from jinja2 import Template

from pysqa.wrapper.abstract import SchedulerCommands

# Slurm job states which indicate the job is still active, see "JOB STATE CODES" in "man squeue".
_slurm_pending_states = {
    "PENDING",
    "CONFIGURING",
    "REQUEUED",
    "RESV_DEL_HOLD",
    "REQUEUE_FED",
    "REQUEUE_HOLD",
}
_slurm_running_states = {
    "RUNNING",
    "COMPLETING",
    "RESIZING",
    "SUSPENDED",
    "STOPPED",
    "SIGNALING",
    "STAGE_OUT",
}

template = """\
#!/bin/bash
#SBATCH --output=time.out
#SBATCH --job-name={{job_name}}
#SBATCH --chdir={{working_directory}}
#SBATCH --get-user-env=L
#SBATCH --partition={{partition}}
{%- if run_time_max %}
#SBATCH --time={{ [1, run_time_max // 60]|max }}
{%- endif %}
{%- if dependency_list %}
#SBATCH --dependency=afterok:{{ dependency_list | join(',') }}
{%- endif %}
{%- if memory_max %}
#SBATCH --mem={{memory_max}}G
{%- endif %}
#SBATCH --ntasks={{cores}}

{{command}}
"""


class SlurmCommands(SchedulerCommands):
    @property
    def submit_job_command(self) -> list[str]:
        """Returns the command to submit a job to Slurm."""
        return ["sbatch", "--parsable"]

    @property
    def delete_job_command(self) -> list[str]:
        """Returns the command to delete a job from Slurm."""
        return ["scancel"]

    @property
    def get_queue_status_command(self) -> list[str]:
        """Returns the command to get the queue status from Slurm."""
        return ["squeue", "--format", "%A|%u|%t|%.15j|%Z", "--noheader"]

    def get_job_status_command(self, process_id: int) -> list[str]:
        """Returns the command to get the status of a single job from the Slurm accounting database."""
        return [
            "sacct",
            "--noheader",
            "--parsable2",
            "--allocations",
            "--format=State",
            "--jobs",
            str(process_id),
        ]

    @staticmethod
    def convert_job_status(job_status_output: str) -> str | None:
        """
        Converts the output of the Slurm accounting command sacct to the pysqa job status. Successfully completed
        jobs are reported as "finished", jobs which terminated in any other way (failed, cancelled, timeout, out of
        memory, node failure, ...) are reported as "error".
        """
        for line in job_status_output.splitlines():
            line_split = line.strip().split()
            if len(line_split) > 0:
                state = line_split[0].upper()
                if state == "COMPLETED":
                    return "finished"
                elif state in _slurm_running_states:
                    return "running"
                elif state in _slurm_pending_states:
                    return "pending"
                else:
                    return "error"
        return None

    @staticmethod
    def get_job_id_from_output(queue_submit_output: str) -> int:
        """Extracts the job ID from the output of the job submission command."""
        return int(queue_submit_output.splitlines()[-1].rstrip().lstrip().split()[-1])

    @staticmethod
    def convert_queue_status(queue_status_output: str) -> pandas.DataFrame:
        """Converts the queue status output from Slurm into a pandas DataFrame."""
        line_split_lst = [line.split("|") for line in queue_status_output.splitlines()]
        if len(line_split_lst) != 0:
            job_id_lst, user_lst, status_lst, job_name_lst, working_directory_lst = zip(
                *[
                    (int(jobid), user, status.lower(), jobname, working_directory)
                    for jobid, user, status, jobname, working_directory in line_split_lst
                ],
                strict=True,
            )
        else:
            job_id_lst, user_lst, status_lst, job_name_lst, working_directory_lst = (
                (),
                (),
                (),
                (),
                (),
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
        df.loc[df.status == "r", "status"] = "running"
        df.loc[df.status == "pd", "status"] = "pending"
        return df

    @staticmethod
    def dependencies(dependency_list: list[str]) -> list[str]:
        """Returns the dependency options for job submission."""
        if dependency_list is not None and len(dependency_list) > 0:
            return ["--dependency=afterok:" + ",".join(dependency_list)]
        else:
            return []

    @staticmethod
    def render_submission_template(
        command: str,
        submission_template: str | Template = template,
        job_name: str = "pysqa",
        working_directory: str = os.path.abspath("."),
        cores: int = 1,
        memory_max: int | str | None = None,
        run_time_max: int | None = None,
        dependency_list: list[int] | None = None,
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
        return SchedulerCommands.render_submission_template(
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
