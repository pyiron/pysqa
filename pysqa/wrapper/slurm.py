# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.
# Updated for HPC UGent by Sander Borgmans

import os
import pandas
from .. import queueadapter as qa

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
          return int(queue_submit_output.splitlines()[-1].rstrip().lstrip().split(';')[0])

    @staticmethod
    def get_queue_from_output(queue_submit_output):
          return str(queue_submit_output.splitlines()[-1].rstrip().lstrip().split(';')[1])

    @staticmethod
    def convert_queue_status(queue_status_output):
        qstat = queue_status_output.splitlines()
        queue = qstat[0].split(':')[1].strip() # get queue name
        if len(qstat) <= 1: # first row contains cluster name, check if there are jobs
            return pandas.DataFrame(columns=['cluster', 'jobid', 'user', 'status', 'jobname'])

        line_split_lst = [line.split('|') for line in qstat[1:]]
        job_id_lst, user_lst, status_lst, job_name_lst, queue_lst = zip(*[(int(jobid), user, status.lower(), jobname, queue)
                                                               for jobid, user, status, jobname in line_split_lst])
        return pandas.DataFrame({'cluster': queue_lst,
                                 'jobid': job_id_lst,
                                 'user': user_lst,
                                 'jobname': job_name_lst,
                                 'status': status_lst})


class QueueAdapterUGent(qa.QueueAdapter):
    """
    The goal of the QueueAdapterUGent class is to overwrite certain functions of the QueueAdapter specific to HPC UGent
    """

    def submit_job(self, queue=None, job_name=None, working_directory=None, cores=None, nodes=None, memory_max=None,
                   run_time_max=None, command=None):
        """

        Args:
            queue (str/None): identifies cluster, if None current cluster is used
            job_name (str/None):
            working_directory (str/None):
            cores (int/str/None): cores per node (int, 'half', 'all')
            nodes (int/None): number of nodes
            memory_max (int/None):
            run_time_max (int/None):
            command (str/None):

        Returns:
            int:
        """
        if isinstance(command, list):
            command = ''.join(command)
        if working_directory is None:
            working_directory = '.'
        queue_script = self._job_submission_template(queue=queue, job_name=job_name,
                                                     working_directory=working_directory, cores=cores, nodes=nodes,
                                                     memory_max=memory_max, run_time_max=run_time_max, command=command)
        queue_script_path = os.path.join(working_directory, 'run_queue.sh')
        with open(queue_script_path, 'w') as f:
            f.writelines(queue_script)
        out = self._execute_command(commands_lst=self._commands.submit_job_command + [queue_script_path],
                                    working_directory=working_directory, split_output=False, queue=queue)
        if out is not None:
            return self._commands.get_job_id_from_output(out)
        else:
            return None

    def enable_reservation(self, process_id, reservation_flag, queue=None):
        """

        Args:
            process_id (int):
            reservation_flag (int): reservation id
            queue (str/None):

        Returns:
            str:
        """
        out = self._execute_command(commands_lst=self._commands.enable_reservation_command + ['x=FLAGS:ADVRES:'+reservation_flag] + [str(process_id)],
                                    split_output=True, queue=queue)
        if out is not None:
            return out[0]
        else:
            return None

    def delete_job(self, process_id, queue=None):
        """

        Args:
            process_id (int):
            queue (str/None):

        Returns:
            str:
        """
        out = self._execute_command(commands_lst=self._commands.delete_job_command + [str(process_id)],
                                    split_output=True, queue=queue)
        if out is not None:
            return out[0]
        else:
            return None

    def get_queue_status(self, user=None, queue=None):
        """

        Args:
            user (str):

        Returns:
            pandas.DataFrame:
        """
        out = self._execute_command(commands_lst=self._commands.get_queue_status_command, split_output=False, queue=queue)
        df = self._commands.convert_queue_status(queue_status_output=out)
        if user is None or df.empty:
            return df
        else:
            return df[df['user'] == user]

    def get_status_of_my_jobs(self):
        """

        Returns:
           pandas.DataFrame:
        """
        df = pandas.DataFrame()

        for queue in self.queue_list:
            user = self._get_user()
            df = df.append(self.get_queue_status(user=user, queue=queue), ignore_index=True, sort=False)
        return df

    def get_status_of_job(self, process_id, queue=None):
        """

        Args:
            process_id:

        Returns:
             str: ['running', 'pending', 'error']
        """
        df = self.get_queue_status(queue=queue)
        df_selected = df[df['jobid'] == process_id]['status']
        if len(df_selected) != 0:
            return df_selected.values[0]
        else:
            return None

    def check_queue_parameters(self, queue, cores=None, nodes=None, run_time_max=None, memory_max=None, active_queue=None):
        """

        Args:
            queue (str/None):
            cores (int/str/None):
            nodes (int/None):
            run_time_max (int/None):
            memory_max (int/None):
            active_queue (dict):
            can be read from $SLURM_CONF

        Returns:
            list: [cores, nodes, run_time_max, memory_max]
        """
        if active_queue is None:
            active_queue = self._config['queues'][queue]

        if isinstance(cores, str):
            if cores=='half': cores = active_queue['cores_max']/2
            elif cores=='all': cores = active_queue['cores_max']
            else: raise ValueError('This string does not correspond to an alias (half,all)')
        else:
            cores =     self._value_in_range(value=cores, value_min=1,
                                     value_max=active_queue['cores_max'])

        nodes =         self._value_in_range(value=nodes, value_min=1,
                                     value_max=active_queue['nodes_max'])

        run_time_max =  self._value_in_range(value=run_time_max,
                                     value_max=active_queue['run_time_max'])

        memory_max =    self._value_in_range(value=memory_max,
                                     value_max=active_queue['pmem_max'])
        return cores, nodes, run_time_max, memory_max

    def _job_submission_template(self, queue=None, job_name=None, working_directory='.', cores=None,
                                 nodes=None, memory_max=None, run_time_max=None, command=None):
        """

        Args:
            queue (str/None):
            job_name (str):
            working_directory (str):
            cores (int/str/None):
            nodes (int/None)
            memory_max (int/None):
            run_time_max (int/None):
            command (str/None):

        Returns:
            str:
        """
        if queue is None:
            queue = os.environ['HPCUGENT_FAMILY_CLUSTER_VERSION'] # get current cluster name
        self._value_error_if_none(value=command)
        if queue not in self.queue_list:
            raise ValueError()
        active_queue = self._config['queues'][queue]
        cores, nodes, run_time_max, memory_max = self.check_queue_parameters(queue=queue,
                                                                      cores=cores,
                                                                      nodes=nodes,
                                                                      run_time_max=run_time_max,
                                                                      memory_max=memory_max,
                                                                      active_queue=active_queue)
        memory_max = str(memory_max)+'MB'
        run_time_max = self._runtime2str(run_time_max)

        template = active_queue['template']
        return template.render(job_name=job_name,
                               working_directory=working_directory,
                               cores=cores,
                               nodes=nodes,
                               memory_max=memory_max,
                               run_time_max=run_time_max,
                               command=command)

    @staticmethod
    def _execute_command(commands_lst, working_directory=None, split_output=True, queue=None):
        """

        Args:
            commands_lst (list):
            working_directory (str):
            split_output (bool):

        Returns:
            str:
        """

        cmd = ""
        if not queue is None:
            cmd += "module --quiet swap cluster/{}; ".format(queue)
        cmd += " ".join(commands_lst)

        if working_directory is None:
            try:
                out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError:
                out = None
        else:
            try:
                out = subprocess.check_output(cmd, cwd=working_directory, stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError:
                out = None

        out = out.decode('utf8')
        if out is not None and split_output:
            return out.split('\n')
        else:
            return out

        @staticmethod
    def _fill_queue_dict(queue_lst_dict):
        """

        Args:
            queue_lst_dict (dict):
        """
        queue_keys = ['cores_max', 'nodes_max', 'pmem_max', 'run_time_max']
        for queue_dict in queue_lst_dict.values():
            for key in set(queue_keys) - set(queue_dict.keys()):
                queue_dict[key] = None

    @staticmethod
    def _runtime2str(time):
        if isinstance(time, int):
            return "{}:{}:{}".format(int(time//3600),int((time%3600)//60),int(time%60))
        else:
            return ValueError('The runtime could not be converted to a suitable format!')
