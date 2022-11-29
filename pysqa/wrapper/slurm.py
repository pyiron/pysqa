# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

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


class SlurmCommands(SchedulerCommands):
    @property
    def submit_job_command(self):
        return ["sbatch", "--parsable"]

    @property
    def delete_job_command(self):
        return ["scancel"]

    @property
    def get_queue_status_command(self):
        return ["squeue", "--format", "%A|%u|%t|%.15j|%Z", "--noheader"]

    @staticmethod
    def get_job_id_from_output(queue_submit_output):
        return int(queue_submit_output.splitlines()[-1].rstrip().lstrip().split()[-1])

    @staticmethod
    def convert_queue_status(queue_status_output):
        line_split_lst = [line.split("|") for line in queue_status_output.splitlines()]
        if len(line_split_lst) != 0:
            job_id_lst, user_lst, status_lst, job_name_lst, working_directory_lst = zip(
                *[
                    (int(jobid), user, status.lower(), jobname, working_directory)
                    for jobid, user, status, jobname, working_directory in line_split_lst
                ]
            )
        else:
            job_id_lst, user_lst, status_lst, job_name_lst, working_directory_lst = (
                [],
                [],
                [],
                [],
                [],
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
    def dependencies(dependency_list) -> list:
        if dependency_list is not None:
            return ["--dependency=afterok:" + ",".join(dependency_list)]
        else:
            return []
