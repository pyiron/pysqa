# coding: utf-8
# Copyright (c) Jan Janssen


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
