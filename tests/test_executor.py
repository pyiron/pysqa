import os
from queue import Queue
from concurrent.futures import Future, ThreadPoolExecutor
import unittest

from pysqa.executor.backend import execute_files_from_list
from pysqa.executor.executor import Executor
from pysqa.executor.helper import (
    read_from_file,
    deserialize,
    serialize_funct,
    write_to_file,
    serialize_result,
    reload_previous_futures,
    _get_file_name,
    _set_future,
    _update_task_dict,
)
from pysqa.queueadapter import QueueAdapter


def funct_add(a, b):
    return a + b


@unittest.skipIf(os.name == "nt", "Runs forever on Windows")
class TestExecutorHelper(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "cache"
        )
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        for f in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, f))
        os.removedirs(self.test_dir)

    def test_cache(self):
        funct_dict = serialize_funct(fn=funct_add, a=1, b=2)
        file_name_in = write_to_file(
            funct_dict=funct_dict, state="in", cache_directory=self.test_dir
        )[0]
        self.assertEqual(len(os.listdir(self.test_dir)), 1)
        funct_dict = read_from_file(file_name=os.path.join(self.test_dir, file_name_in))
        apply_dict = deserialize(funct_dict=funct_dict)
        key = list(apply_dict.keys())[0]
        v = apply_dict[key]
        result_dict = {key: v["fn"].__call__(*v["args"], **v["kwargs"])}
        file_name_out = write_to_file(
            funct_dict=serialize_result(result_dict=result_dict),
            state="out",
            cache_directory=self.test_dir,
        )[0]
        self.assertEqual(len(os.listdir(self.test_dir)), 2)
        f = Future()
        _set_future(file_name=os.path.join(self.test_dir, file_name_out), future=f)
        self.assertEqual(f.result(), 3)
        task_dict = {key: Future()}
        _update_task_dict(
            task_dict=task_dict, task_memory_dict={}, cache_directory=self.test_dir
        )
        self.assertEqual(task_dict[key].result(), 3)

    def test_reload_previous_future(self):
        funct_dict = serialize_funct(fn=funct_add, a=1, b=2)
        file_name_in = write_to_file(
            funct_dict=funct_dict, state="in", cache_directory=self.test_dir
        )[0]
        queue = Queue()
        future_dict_one = {}
        reload_previous_futures(
            future_queue=queue,
            future_dict=future_dict_one,
            cache_directory=self.test_dir,
        )
        self.assertEqual(len(future_dict_one), 1)
        self.assertEqual(
            list(future_dict_one.keys())[0], file_name_in.split(".in.pl")[0]
        )
        self.assertEqual(len(os.listdir(self.test_dir)), 1)
        with ThreadPoolExecutor() as exe:
            execute_files_from_list(
                tasks_in_progress_dict={}, cache_directory=self.test_dir, executor=exe
            )
        self.assertEqual(len(os.listdir(self.test_dir)), 2)
        future_dict_two = {}
        reload_previous_futures(
            future_queue=queue,
            future_dict=future_dict_two,
            cache_directory=self.test_dir,
        )
        key = list(future_dict_two.keys())[0]
        self.assertEqual(len(future_dict_two), 1)
        self.assertEqual(key, file_name_in.split(".in.pl")[0])
        self.assertEqual(future_dict_two[key].result(), 3)


class TestExecutor(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "executor_cache"
        )
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        for f in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, f))
        os.removedirs(self.test_dir)

    def test_executor(self):
        def execute_command(
            commands,
            working_directory=None,
            split_output=True,
            shell=False,
            error_filename="pysqa.err",
        ):
            return str(1)

        queue_adapter = QueueAdapter(
            directory=os.path.join(self.test_dir, "../config/slurm"),
            execute_command=execute_command,
        )
        with Executor(
            cwd=self.test_dir,
            queue_adapter=queue_adapter,
            queue_adapter_kwargs={"queue": "slurm", "job_name": "test", "cores": 1},
        ) as exe:
            fs = exe.submit(fn=funct_add, a=1, b=2)
            funct_dict = serialize_funct(fn=funct_add, a=1, b=2)
            file_name_in = _get_file_name(name=list(funct_dict.keys())[0], state="in")
            funct_dict = read_from_file(
                file_name=os.path.join(self.test_dir, file_name_in)
            )
            apply_dict = deserialize(funct_dict=funct_dict)
            result_dict = {
                k: v["fn"].__call__(*v["args"], **v["kwargs"])
                for k, v in apply_dict.items()
            }
            _ = write_to_file(
                funct_dict=serialize_result(result_dict=result_dict),
                state="out",
                cache_directory=self.test_dir,
            )[0]
            self.assertEqual(fs.result(), 3)
