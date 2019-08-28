# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import pandas
from pysqa.wrapper.slurm import SlurmCommands


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


class GentCommands(SlurmCommands):
    @staticmethod
    def get_job_id_from_output(queue_submit_output):
          return int(queue_submit_output.splitlines()[-1].rstrip().lstrip().split(';')[0])

    @staticmethod
    def get_queue_from_output(queue_submit_output):
          return str(queue_submit_output.splitlines()[-1].rstrip().lstrip().split(';')[1])

    @staticmethod
    def convert_queue_status(queue_status_output):
        qstat = queue_status_output.splitlines()
        queue = qstat[0].split(':')[1].strip()
        if len(qstat) <= 1: # first row contains cluster name, check if there are jobs
            return None

        line_split_lst = [line.split('|') for line in qstat[1:]]
        job_id_lst, user_lst, status_lst, job_name_lst, queue_lst = zip(*[(int(jobid), user, status.lower(), jobname, queue)
                                                               for jobid, user, status, jobname in line_split_lst])
        return pandas.DataFrame({'cluster': queue_lst,
                                 'jobid': job_id_lst,
                                 'user': user_lst,
                                 'jobname': job_name_lst,
                                 'status': status_lst})
