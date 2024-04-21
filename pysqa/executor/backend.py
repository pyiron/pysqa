import os
from typing import Optional
import sys

from pympipool import Executor
from pysqa.executor.helper import (
    read_from_file,
    deserialize,
    write_to_file,
    serialize_result,
)


def execute_files_from_list(
    tasks_in_progress_dict: dict, cache_directory: str, executor
):
    file_lst = os.listdir(cache_directory)
    for file_name_in in file_lst:
        key = file_name_in.split(".in.pl")[0]
        file_name_out = key + ".out.pl"
        if (
            file_name_in.endswith(".in.pl")
            and file_name_out not in file_lst
            and key not in tasks_in_progress_dict.keys()
        ):
            funct_dict = read_from_file(
                file_name=os.path.join(cache_directory, file_name_in)
            )
            apply_dict = deserialize(funct_dict=funct_dict)
            for k, v in apply_dict.items():
                tasks_in_progress_dict[k] = executor.submit(
                    v["fn"], *v["args"], **v["kwargs"]
                )
    for k, v in tasks_in_progress_dict.items():
        if v.done():
            write_to_file(
                funct_dict=serialize_result(result_dict={k: v.result()}),
                state="out",
                cache_directory=cache_directory,
            )


def execute_tasks(cores: int, cache_directory: str):
    tasks_in_progress_dict = {}
    with Executor(
        max_cores=cores,
        cores_per_worker=1,
        threads_per_core=1,
        gpus_per_worker=0,
        oversubscribe=False,
        init_function=None,
        cwd=cache_directory,
        backend="mpi",
    ) as exe:
        while True:
            execute_files_from_list(
                tasks_in_progress_dict=tasks_in_progress_dict,
                cache_directory=cache_directory,
                executor=exe,
            )


def command_line(arguments_lst: Optional[list] = None):
    if arguments_lst is None:
        arguments_lst = sys.argv[1:]
    cores_arg = arguments_lst[arguments_lst.index("--cores") + 1]
    path_arg = arguments_lst[arguments_lst.index("--path") + 1]
    execute_tasks(cores=cores_arg, cache_directory=path_arg)
