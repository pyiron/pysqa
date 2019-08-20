# coding: utf-8
# Copyright (c) Jan Janssen


class QueueAdapterInterface(object):
    # Functions which need to be implemented for each QueueAdapter
    def __init__(self, config, directory='~/.queues'):
       raise NotImplementedError

    @property
    def config(self):
        """

        Returns:
            dict:
        """
        raise NotImplementedError

    @property
    def queue_list(self):
        """

        Returns:
            list:
        """
        raise NotImplementedError

    @property
    def queue_view(self):
        """

        Returns:
            pandas.DataFrame:
        """
        raise NotImplementedError

    @property
    def queues(self):
        raise NotImplementedError

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
        raise NotImplementedError

    def enable_reservation(self, process_id):
        """

        Args:
            process_id (int):

        Returns:
            str:
        """
        raise NotImplementedError

    def delete_job(self, process_id):
        """

        Args:
            process_id (int):

        Returns:
            str:
        """
        raise NotImplementedError

    def get_queue_status(self, user=None):
        """

        Args:
            user (str):

        Returns:
            pandas.DataFrame:
        """
        raise NotImplementedError

    def get_status_of_my_jobs(self):
        """

        Returns:
           pandas.DataFrame:
        """
        raise NotImplementedError

    def get_status_of_job(self, process_id):
        """

        Args:
            process_id:

        Returns:
             str: ['running', 'pending', 'error']
        """
        raise NotImplementedError

    def get_status_of_jobs(self, process_id_lst):
        """

        Args:
            process_id_lst:

        Returns:
             list: ['running', 'pending', 'error', ...]
        """
        raise NotImplementedError

    def check_queue_parameters(self, queue, cores=1, run_time_max=None, memory_max=None, active_queue=None):
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
        raise NotImplementedError
