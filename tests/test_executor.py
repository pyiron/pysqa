import os
from concurrent.futures import Future
import unittest

from pysqa.executor.helper import (
    read_from_file,
    deserialize,
    serialize_funct,
    write_to_file,
    serialize_result,
    set_future,
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
        file_name_in = write_to_file(funct_dict=funct_dict, state="in", cache_directory=self.test_dir)[0]
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
