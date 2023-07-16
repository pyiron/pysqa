import os
from queue import Queue
from concurrent.futures import Future, ThreadPoolExecutor
import unittest

from pysqa.executor.backend import execute_files_from_list
from pysqa.executor.helper import (
    read_from_file,
    deserialize,
    serialize_funct,
    write_to_file,
    serialize_result,
    set_future,
    reload_previous_futures
)


def funct_add(a, b):
    return a+b


class TestExecutorHelper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.abspath(os.path.dirname(__file__))
        os.makedirs(os.path.join(cls.test_dir, "cache"), exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        os.removedirs(os.path.join(cls.test_dir, "cache"))

    def test_cache(self):
        funct_dict = serialize_funct(fn=funct_add, a=1, b=2)
        file_name_in = write_to_file(
            funct_dict=funct_dict,
            state="in",
            cache_directory=self.test_dir
        )[0]
        funct_dict = read_from_file(
            file_name=os.path.join(self.test_dir, file_name_in)
        )
        apply_dict = deserialize(funct_dict=funct_dict)
        result_dict = {
            k: v["fn"].__call__(*v["args"], **v["kwargs"]) for k, v in apply_dict.items()
        }
        file_name_out = write_to_file(
            funct_dict=serialize_result(result_dict=result_dict),
            state="out",
            cache_directory=self.test_dir,
        )[0]
        f = Future()
        set_future(
            file_name=os.path.join(self.test_dir, file_name_out), 
            future=f
        )
        self.assertEqual(f.result(), 3)

    def test_reload_previous_future(self):
        funct_dict = serialize_funct(fn=funct_add, a=1, b=2)
        file_name_in = write_to_file(
            funct_dict=funct_dict,
            state="in",
            cache_directory=self.test_dir
        )[0]
        queue = Queue()
        future_dict_one = {}
        reload_previous_futures(
            future_queue=queue,
            future_dict=future_dict_one,
            cache_directory=self.test_dir
        )
        self.assertEqual(len(future_dict_one), 1)
        self.assertEqual(list(future_dict_one.keys())[0], file_name_in.split(".in.pl")[0])
        with ThreadPoolExecutor() as exe:
            execute_files_from_list(
                tasks_in_progress_dict={},
                cache_directory=self.test_dir,
                executor=exe
            )
        future_dict_two = {}
        reload_previous_futures(
            future_queue=queue,
            future_dict=future_dict_two,
            cache_directory=self.test_dir
        )
        key = list(future_dict_two.keys())[0]
        self.assertEqual(len(future_dict_two), 1)
        self.assertEqual(key, file_name_in.split(".in.pl")[0])
        self.assertEqual(future_dict_two[key].result(), 3)
