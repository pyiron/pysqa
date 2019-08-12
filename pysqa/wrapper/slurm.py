# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import pandas


__author__ = "Jan Janssen"
__copyright__ = "Copyright 2019, Max-Planck-Institut für Eisenforschung GmbH - " \
                "Computational Materials Design (CM) Department"
__version__ = "1.0"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "development"
__date__ = "Feb 9, 2019"


class SlurmCommands(object):
    @property
    def submit_job_command(self):
        return ['sbatch', '--parsable']

    @property
    def delete_job_command(self):
        return ['scancel']

    @property
    def enable_reservation_command(self): # this is written in TORQUE (compatible with hpc)
        return ['qalter', '-W']

    @property
    def get_queue_status_command(self):
        return ['squeue', '--format', '"%A|%u|%t|%j"', '--noheader']

    @staticmethod
    def get_job_id_from_output(queue_submit_output):
          return int(queue_submit_output.splitlines()[-1].rstrip().lstrip().split(';')[0])  # adapted here (gives string jobid;cluster instead of jobid)

    @staticmethod
    def get_queue_from_output(queue_submit_output):
          return str(queue_submit_output.splitlines()[-1].rstrip().lstrip().split(';')[1])

    @staticmethod
    def convert_queue_status(queue_status_output):
        qstat = queue_status_output.splitlines()
        queue = qstat[0].split(':')[1].strip() # get queue name for pandas dataframe
        if len(qstat[1:]) == 0: # if empty
            return None

        line_split_lst = [line.split('|') for line in qstat[1:]] # adapted here (starts from 1 since first line gives cluster)
        job_id_lst, user_lst, status_lst, job_name_lst, queue_lst = zip(*[(int(jobid), user, status.lower(), jobname, queue)
                                                               for jobid, user, status, jobname in line_split_lst])
        return pandas.DataFrame({'cluster': queue_lst,
                                 'jobid': job_id_lst,
                                 'user': user_lst,
                                 'jobname': job_name_lst,
                                 'status': status_lst})
