# coding: utf-8
# Copyright (c) Jan Janssen
# Updated for HPC UGent by Sander Borgmans

import getpass
import importlib
from jinja2 import Template
import os
import pandas
import subprocess
import yaml

__author__ = "Jan Janssen"
__copyright__ = "Copyright 2019, Jan Janssen"
__version__ = "0.0.1"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "production"
__date__ = "Feb 9, 2019"


class QueueAdapter(object):
    """
    The goal of the QueueAdapter class is to make submitting to a queue system as easy as starting another sub process
    locally.

    Args:
        directory (str): directory containing the queue.yaml files as well as corresponding jinja2 templates for the
                         individual queues.

    Attributes:

        .. attribute:: config

            QueueAdapter configuration read from the queue.yaml file.

        .. attribute:: queue_list

            List of available queues

        .. attribute:: queue_view

            Pandas DataFrame representation of the available queues, read from queue.yaml.

        .. attribute:: queues

            Queues available for auto completion QueueAdapter().queues.<queue name> returns the queue name.
    """
    def __init__(self, directory='~/.queues'):
        self._config = self._read_config(file_name=os.path.join(directory, 'queue.yaml'))
        self._fill_queue_dict(queue_lst_dict=self._config['queues'])
        self._load_templates(queue_lst_dict=self._config['queues'], directory=directory)
        if self._config['queue_type'] == 'SGE':
            class_name = 'SunGridEngineCommands'
            module_name = 'pysqa.wrapper.sge'
        elif self._config['queue_type'] == 'TORQUE':
            class_name = 'TorqueCommands'
            module_name = 'pysqa.wrapper.torque'
        elif self._config['queue_type'] == 'SLURM':
            class_name = 'SlurmCommands'
            module_name = 'pysqa.wrapper.slurm'
        elif self._config['queue_type'] == 'LSF':
            class_name = 'LsfCommands'
            module_name = 'pysqa.wrapper.lsf'
        elif self._config['queue_type'] == 'MOAB':
            class_name = 'MoabCommands'
            module_name = 'pysqa.wrapper.moab'
        else:
            raise ValueError()
        self._commands = getattr(importlib.import_module(module_name), class_name)()
        self._queues = Queues(self.queue_list)

    @property
    def config(self):
        """

        Returns:
            dict:
        """
        return self._config

    @property
    def queue_list(self):
        """

        Returns:
            list:
        """
        return list(self._config['queues'].keys())

    @property
    def queue_view(self):
        """

        Returns:
            pandas.DataFrame:
        """
        return pandas.DataFrame(self._config['queues']).T.drop(['script', 'template'], axis=1)

    @property
    def queues(self):
        return self._queues

    def submit_job(self, queue=None, job_name=None, working_directory=None, cores=None, memory_max=None,
                   run_time_max=None, command=None):
        """

        Args:
            queue (str/None):
            job_name (str/None):
            working_directory (str/None):
            cores (int/None):
            memory_max (int/None):
            run_time_max (int/None):
            command (str/None):

        Returns:
            int:
        """
        if isinstance(command, list):
            command = ''.join(command)

        queue_script = self._job_submission_template(queue=queue, job_name=job_name,
                                                     working_directory=working_directory, cores=cores,
                                                     memory_max=memory_max, run_time_max=run_time_max, command=command)
        queue_script_path = os.path.join(working_directory, 'run_queue.sh')
        with open(queue_script_path, 'w') as f:
            f.writelines(queue_script)
        out = self._execute_command(commands_lst=self._commands.submit_job_command + [queue_script_path],
                                    working_directory=working_directory, split_output=False, queue=queue) # adapted
        if out is not None:
            return self._commands.get_job_id_from_output(out)
        else:
            return None

    def enable_reservation(self, process_id, reservation_flag, queue=None): # not implemented I guess
        """

        Args:
            process_id (int):

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

    def check_queue_parameters(self, queue, cores=None, run_time_max=None, memory_max=None, active_queue=None): #adapted
        """

        Args:
            queue (str/None):
            cores (int):
            run_time_max (int/None):
            memory_max (int/None):
            active_queue (dict):

        Returns:
            list: [cores, run_time_max, memory_max]
        """
        if active_queue is None:
            active_queue = self._config['queues'][queue]
        cores = self._value_in_range(value=cores,
                                     value_min=active_queue['cores_min'],
                                     value_max=active_queue['cores_max'])

        nodes = (cores-1)//(active_queue['cores_per_node']) + 1

        run_time_max = self._value_in_range(value=run_time_max,
                                            value_max=active_queue['run_time_max'])

        memory_max = self._value_in_range(value=memory_max, # assume in bytes!
                                          value_max=active_queue['mem_per_node_max']*nodes*1024**3)
        return cores, run_time_max, memory_max

    def _job_submission_template(self, queue=None, job_name=None, working_directory='.', cores=None,
                                 memory_max=None, run_time_max=None, command=None):
        """

        Args:
            queue (str/None):
            job_name (str):
            working_directory (str):
            cores (int/None):
            memory_max (int/None):
            run_time_max (int/None):
            command (str/None):

        Returns:
            str:
        """
        if queue is None:
            queue = self._config['queue_primary']
        self._value_error_if_none(value=command)
        if queue not in self.queue_list:
            raise ValueError()
        active_queue = self._config['queues'][queue]
        cores, run_time_max, memory_max = self.check_queue_parameters(queue=queue,
                                                                      cores=cores,
                                                                      run_time_max=run_time_max,
                                                                      memory_max=memory_max,
                                                                      active_queue=active_queue)
        nodes = (cores-1)//(active_queue['cores_per_node']) + 1
        cores = int((cores-1)%active_queue['cores_per_node']) + 1
        memory_max = self._get_size(memory_max) + 'B'
        run_time_max = "{}:{}:{}".format(int(run_time_max//3600),int((run_time_max%3600)//60),int(run_time_max%60))

        template = active_queue['template']
        return template.render(job_name=job_name,
                               working_directory=working_directory,
                               cores=cores,
                               nodes=nodes,
                               memory_max=memory_max,
                               run_time_max=run_time_max,
                               command=command)

    @staticmethod
    def _get_user():
        """

        Returns:
            str:
        """
        return getpass.getuser()

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
    def _read_config(file_name='queue.yaml'):
        """

        Args:
            file_name (str):

        Returns:
            dict:
        """
        with open(file_name, 'r') as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    @staticmethod
    def _fill_queue_dict(queue_lst_dict):
        """

        Args:
            queue_lst_dict (dict):
        """
        queue_keys = ['cores_min', 'cores_max', 'run_time_max', 'memory_max']
        for queue_dict in queue_lst_dict.values():
            for key in set(queue_keys) - set(queue_dict.keys()):
                queue_dict[key] = None

    @staticmethod
    def _load_templates(queue_lst_dict, directory='.'):
        """

        Args:
            queue_lst_dict (dict):
            directory (str):
        """
        for queue_dict in queue_lst_dict.values():
            with open(os.path.join(directory, queue_dict['script']), 'r') as f:
                queue_dict['template'] = Template(f.read())

    @staticmethod
    def _value_error_if_none(value):
        """

        Args:
            value (str/None):
        """
        if value is None:
            raise ValueError()
        if not isinstance(value, str):
            raise TypeError()

    @staticmethod
    def _value_in_range(value, value_min=None, value_max=None):
        """

        Args:
            value (int/float/None):
            value_min (int/float/None):
            value_max (int/float/None):

        Returns:
            int/float/None:
        """
        if value is not None:
            if value_min is not None and value < value_min:
                return value_min
            if value_max is not None and value > value_max:
                return value_max
            return value
        else:
            if value_min is not None:
                return value_min
            if value_max is not None:
                return value_max
            return value

    @staticmethod
    def _get_size(size):
        system = [
        (1024 ** 5, 'P'),
        (1024 ** 4, 'T'),
        (1024 ** 3, 'G'),
        (1024 ** 2, 'M'),
        (1024 ** 1, 'K'),
        (1024 ** 0, 'B'),
        ]
        for factor, suffix in system:
            if size >= factor:
                break
        amount = int(size/factor)
        return str(amount) + suffix


class Queues(object):
    """
    Queues is an abstract class simply to make the list of queues available for auto completion. This is mainly used in
    interactive environments like jupyter.
    """
    def __init__(self, list_of_queues):
        self._list_of_queues = list_of_queues

    def __getattr__(self, item):
        if item in self._list_of_queues:
            return item
        else:
            raise AttributeError

    def __dir__(self):
        return self._list_of_queues
