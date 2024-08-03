from typing import List


class Queues(object):
    """
    Queues is an abstract class simply to make the list of queues available for auto completion. This is mainly used in
    interactive environments like jupyter.
    """

    def __init__(self, list_of_queues: List[str]):
        """
        Initialize the Queues object.

        Args:
            list_of_queues (List[str]): A list of queue names.

        """
        self._list_of_queues = list_of_queues

    def __getattr__(self, item: str) -> str:
        """
        Get the queue name.

        Args:
            item (str): The name of the queue.

        Returns:
            str: The name of the queue.

        Raises:
            AttributeError: If the queue name is not in the list of queues.

        """
        if item in self._list_of_queues:
            return item
        else:
            raise AttributeError

    def __dir__(self) -> List[str]:
        """
        Get the list of queues.

        Returns:
            List[str]: The list of queues.

        """
        return self._list_of_queues
