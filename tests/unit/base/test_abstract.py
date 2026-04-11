import unittest
from unittest.mock import patch
from pysqa.base.abstract import QueueAdapterAbstractClass


class TestQueueAdapterAbstractClass(unittest.TestCase):
    @patch.multiple(QueueAdapterAbstractClass, __abstractmethods__=set())
    def test_submit_job(self):
        self.assertIsNone(QueueAdapterAbstractClass().submit_job())

    @patch.multiple(QueueAdapterAbstractClass, __abstractmethods__=set())
    def test_enable_reservation(self):
        self.assertIsNone(QueueAdapterAbstractClass().enable_reservation(process_id=1))

    @patch.multiple(QueueAdapterAbstractClass, __abstractmethods__=set())
    def test_delete_job(self):
        self.assertIsNone(QueueAdapterAbstractClass().delete_job(process_id=1))

    @patch.multiple(QueueAdapterAbstractClass, __abstractmethods__=set())
    def test_get_queue_status(self):
        self.assertIsNone(QueueAdapterAbstractClass().get_queue_status())

    @patch.multiple(QueueAdapterAbstractClass, __abstractmethods__=set())
    def test_get_status_of_my_jobs(self):
        self.assertIsNone(QueueAdapterAbstractClass().get_status_of_my_jobs())

    @patch.multiple(QueueAdapterAbstractClass, __abstractmethods__=set())
    def test_get_status_of_job(self):
        self.assertIsNone(QueueAdapterAbstractClass().get_status_of_job(process_id=1))

    @patch.multiple(QueueAdapterAbstractClass, __abstractmethods__=set())
    def test_get_status_of_jobs(self):
        self.assertIsNone(QueueAdapterAbstractClass().get_status_of_jobs(process_id_lst=[1]))