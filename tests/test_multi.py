# coding: utf-8
# Copyright (c) Jan Janssen

import os
import unittest
from pysqa import QueueAdapter

__author__ = "Jan Janssen"
__copyright__ = "Copyright 2019, Jan Janssen"
__version__ = "0.0.1"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "production"
__date__ = "Feb 9, 2019"


class TestMultiQueueAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.dirname(os.path.abspath(__file__))
        cls.multi = QueueAdapter(directory=os.path.join(cls.path, "config/multicluster"))

    def test_config(self):
        self.assertEqual(self.multi.config["queue_type"], "SLURM")
        self.assertEqual(self.multi.config["queue_primary"], "slurm")

    def test_list_clusters(self):
        self.assertEqual(self.multi.list_clusters(), ['local_slurm', 'remote_slurm'])
