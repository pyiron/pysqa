import os
import queue
from typing import Optional
from concurrent.futures import Future, Executor as FutureExecutor

from pympipool.shared import cancel_items_in_queue, RaisingThread
from pysqa.executor.helper import (
    reload_previous_futures,
    find_executed_tasks,
    serialize_funct,
    write_to_file,
)


class Executor(FutureExecutor):
    def __init__(
        self,
        cwd: Optional[str] = None,
        queue_adapter=None,
        queue_adapter_kwargs: Optional[dict] = None,
    ):
        self._task_queue = queue.Queue()
        self._memory_dict = {}
        self._cache_directory = os.path.abspath(os.path.expanduser(cwd))
        self._queue_adapter = queue_adapter
        reload_previous_futures(
            future_queue=self._task_queue,
            future_dict=self._memory_dict,
            cache_directory=self._cache_directory,
        )
        command = (
            "python -m pysqa.executor --cores "
            + str(queue_adapter_kwargs["cores"])
            + " --path "
            + str(self._cache_directory)
        )
        self._queue_id = self._queue_adapter.submit_job(
            working_directory=self._cache_directory,
            command=command,
            **queue_adapter_kwargs,
        )
        self._process = RaisingThread(
            target=find_executed_tasks,
            kwargs={
                "future_queue": self._task_queue,
                "cache_directory": self._cache_directory,
            },
        )
        self._process.start()

    def submit(self, fn: callable, *args, **kwargs):
        funct_dict = serialize_funct(fn, *args, **kwargs)
        key = list(funct_dict.keys())[0]
        if key not in self._memory_dict.keys():
            self._memory_dict[key] = Future()
            _ = write_to_file(
                funct_dict=funct_dict, state="in", cache_directory=self._cache_directory
            )[0]
            self._task_queue.put({key: self._memory_dict[key]})
        return self._memory_dict[key]

    def shutdown(self, wait: bool = True, *, cancel_futures: bool = False):
        if cancel_futures:
            cancel_items_in_queue(que=self._task_queue)
        self._task_queue.put({"shutdown": True, "wait": wait})
        self._queue_adapter.delete_job(process_id=self._queue_id)
        self._process.join()
