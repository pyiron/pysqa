__version__ = "0.0.1"
__all__ = []

from pysqa.queueadapter import QueueAdapter

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
