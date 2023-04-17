# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

from pysqa.wrapper.generic import SchedulerCommands
import subprocess
import pandas as pd

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
    def submit_job_command(self):
        return ["qsub"]

    @property
    def delete_job_command(self):
        return ["qdel"]

    @property
    def get_queue_status_command(self):
        return ["qstat", "-f"]

    @staticmethod
    def get_job_id_from_output(queue_submit_output):
        # strip last line from output, leading and trailing whitespaces, and separates the queue id from the stuff after "."
        # Adjust if your system doesn't have output like below!
        # e.g. qsub run_queue.sh -> "12347673.gadi-pbs", the below returns 12347673
        # It must return an integer for it to not raise an exception later.
        return int(
            queue_submit_output.splitlines()[-1].rstrip().lstrip().split(sep=".")[0]
        )

    @staticmethod
    def convert_queue_status(queue_status_output):

        # # Run the qstat -f command and capture its output
        # output = subprocess.check_output(["qstat", "-f"])
        
        # Split the output into lines
        lines = queue_status_output.decode().split("\n")

        # Extract the job ID, user, job name, status, and working directory for each running job
        job_id = None
        user = None
        job_name = None
        status = None
        working_dir = None
        job_id_lst = []
        user_lst = []
        job_name_lst = []
        status_lst = []
        working_directory_lst = []

        for line in lines:
            if line.startswith("Job Id:"):
                # Start a new job entry
                job_id = line.split()[-1].split(sep=".")[0]
            elif line.startswith("    Job_Name ="):
                job_name = line.split("=")[-1].strip()
            elif line.startswith("    Job_Owner ="):
                user = line.split("=")[-1].split("@")[0]
            elif line.startswith("    job_state ="):
                status = line.split("=")[-1].strip()
            elif "PBS_O_WORKDIR" in line:
                working_dir = line.split()[-1].split(sep="WORKDIR=")[-1]
            elif line.strip() == "":
                # End of job entry - add to lists 
                # This if is necessary to avoid the final row containing None values...
                if all(var is not None for var in (job_id, user, job_name, status, working_dir)):
                    job_id_lst.append(job_id)
                    user_lst.append(user)
                    job_name_lst.append(job_name)
                    status_lst.append(status)
                    working_directory_lst.append(working_dir)
                # Reset variables for next job
                job_id = None
                user = None
                job_name = None
                status = None
                working_dir = None
        # Create a DataFrame from the lists
        df = pd.DataFrame(
            {
                "jobid": job_id_lst,
                "user": user_lst,
                "jobname": job_name_lst,
                "status": status_lst,
                "working_directory": working_directory_lst,
            }
        )
        df["status"] = df["status"].apply(lambda x: "running" if x == "R" else "pending")

        return df