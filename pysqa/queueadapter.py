# coding: utf-8
# Copyright (c) Jan Janssen

import os
from pysqa.utils.functs import read_config, set_queue_adapter

__author__ = "Jan Janssen"
__copyright__ = "Copyright 2019, Jan Janssen"
__version__ = "0.0.3"
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
    def __init__(self, directory="~/.queues"):
        queue_yaml = os.path.join(directory, "queue.yaml")
        clusters_yaml = os.path.join(directory, "clusters.yaml")
        self._adapter = None
        if os.path.exists(queue_yaml):
            self._queue_dict = {
                "default": set_queue_adapter(
                    config=read_config(file_name=queue_yaml),
                    directory=directory
                )
            }
            primary_queue = "default"
        elif os.path.exists(clusters_yaml):
            config = read_config(file_name=clusters_yaml)
            self._queue_dict = {
                k: set_queue_adapter(
                    config=read_config(
                        file_name=os.path.join(directory, v)
                    ),
                    directory=directory
                )
                for k, v in config["cluster"].items()
            }
            primary_queue = config["cluster_primary"]
        else:
            raise ValueError
        self._adapter = self._queue_dict[primary_queue]

    def list_clusters(self):
        """
        List available computing clusters for remote submission

        Returns:
            list: List of computing clusters
        """
        return self._queue_dict.keys()

    def switch_cluster(self, cluster_name):
        """
        Switch to a different computing cluster

        Args:
            cluster_name (str): name of the computing cluster
        """
        self._adapter = self._queue_dict[cluster_name]

    @property
    def config(self):
        """

        Returns:
            dict:
        """
        return self._adapter.config

    @property
    def ssh_delete_file_on_remote(self):
        return self._adapter.ssh_delete_file_on_remote

    @property
    def remote_flag(self):
        """

        Returns:
            bool:
        """
        return self._adapter.remote_flag

    @property
    def queue_list(self):
        """

        Returns:
            list:
        """
        return self._adapter.queue_list

    @property
    def queue_view(self):
        """

        Returns:
            pandas.DataFrame:
        """
        return self._adapter.queue_view

    @property
    def queues(self):
        return self._adapter.queues

    def submit_job(
        self,
        queue=None,
        job_name=None,
        working_directory=None,
        cores=None,
        memory_max=None,
        run_time_max=None,
        command=None,
    ):
        """
        Submits command to the given queue.

        Args:
            queue (str/None):  Name of the queue to submit to, must be one of the names configured for this adapter
            job_name (str/None):  Name of the job for the underlying queuing system
            working_directory (str/None):  Directory to run the job in
            cores (int/None):  Number of hardware threads requested
            memory_max (int/None):  Amount of memory requested per node in GB
            run_time_max (int/None):  Maximum runtime in seconds
            command (str/None):  shell command to run in the job

        Returns:
            int:
        """
        return self._adapter.submit_job(
            queue=queue,
            job_name=job_name,
            working_directory=working_directory,
            cores=cores,
            memory_max=memory_max,
            run_time_max=run_time_max,
            command=command,
        )

    def enable_reservation(self, process_id):
        """

        Args:
            process_id (int):

        Returns:
            str:
        """
        return self._adapter.enable_reservation(process_id=process_id)

    def get_job_from_remote(self, working_directory, delete_remote=False):
        """
        Get the results of the calculation - this is necessary when the calculation was executed on a remote host.

        Args:
            working_directory (str):
            delete_remote (bool):
        """
        self._adapter.get_job_from_remote(working_directory=working_directory, delete_remote=delete_remote)

    def transfer_file_to_remote(self, file, transfer_back=False, delete_remote=False):
        """

        Args:
            file (str):
            transfer_back (bool):
            delete_remote (bool):

        Returns:
            str:
        """
        self._adapter.transfer_file(file=file, transfer_back=transfer_back, delete_remote=delete_remote)

    def convert_path_to_remote(self, path):
        """

        Args:
            path (str):

        Returns:
            str:
        """
        return self._adapter.convert_path_to_remote(path=path)

    def delete_job(self, process_id):
        """

        Args:
            process_id (int):

        Returns:
            str:
        """
        return self._adapter.delete_job(process_id=process_id)

    def get_queue_status(self, user=None):
        """

        Args:
            user (str):

        Returns:
            pandas.DataFrame:
        """
        return self._adapter.get_queue_status(user=user)

    def get_status_of_my_jobs(self):
        """

        Returns:
           pandas.DataFrame:
        """
        return self._adapter.get_status_of_my_jobs()

    def get_status_of_job(self, process_id):
        """

        Args:
            process_id:

        Returns:
             str: ['running', 'pending', 'error']
        """
        return self._adapter.get_status_of_job(process_id=process_id)

    def get_status_of_jobs(self, process_id_lst):
        """

        Args:
            process_id_lst:

        Returns:
             list: ['running', 'pending', 'error', ...]
        """
        return self._adapter.get_status_of_jobs(process_id_lst=process_id_lst)

    def check_queue_parameters(
        self, queue, cores=1, run_time_max=None, memory_max=None, active_queue=None
    ):
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
        return self._adapter.check_queue_parameters(
            queue=queue,
            cores=cores,
            run_time_max=run_time_max,
            memory_max=memory_max,
            active_queue=active_queue,
        )


