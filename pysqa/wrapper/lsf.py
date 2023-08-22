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


class LsfCommands(SchedulerCommands):
    @property
    def submit_job_command(self):
        return ["bsub"]

    @property
    def delete_job_command(self):
        return ["bkill"]

    @property
    def get_queue_status_command(self):
        return ["bjobs"]

    @staticmethod
    def get_job_id_from_output(queue_submit_output):
        return int(queue_submit_output.split("<")[1].split(">")[0])

    @staticmethod
    def convert_queue_status(queue_status_output):
        job_id_lst, user_lst, status_lst, job_name_lst = [], [], [], []
        line_split_lst = queue_status_output.split("\n")
        if len(line_split_lst) > 1:
            for l in line_split_lst[1:]:
                line_segments = l.split()
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
