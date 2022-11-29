# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

from abc import ABC, abstractmethod

__author__ = "Niklas Siemer"
__copyright__ = (
    "Copyright 2022, Max-Planck-Institut für Eisenforschung GmbH - "
    "Computational Materials Design (CM) Department"
)
__version__ = "1.0"
__maintainer__ = "Niklas Siemer"
__email__ = "siemer@mpie.de"
__status__ = "production"
__date__ = "Aug 15, 2022"


class SchedulerCommands(ABC):
    @property
    @abstractmethod
    def submit_job_command(self):
        pass

    @property
    @abstractmethod
    def delete_job_command(self):
        pass

    @property
    def enable_reservation_command(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def get_queue_status_command(self):
        pass

    @staticmethod
    def dependencies(dependency_list) -> list:
        if dependency_list is not None:
            raise NotImplementedError()
        else:
            return []

    @staticmethod
    def get_job_id_from_output(queue_submit_output):
        raise NotImplementedError()

    @staticmethod
    def convert_queue_status(queue_status_output):
        raise NotImplementedError()
