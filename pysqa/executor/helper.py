import os
import re
import queue
from concurrent.futures import Future

import hashlib
import cloudpickle


def deserialize(funct_dict: dict) -> dict:
    try:
        return {k: cloudpickle.loads(v) for k, v in funct_dict.items()}
    except EOFError:
        return {}


def find_executed_tasks(future_queue: queue.Queue, cache_directory: str):
    task_memory_dict = {}
    while True:
        task_dict = {}
        try:
            task_dict = future_queue.get_nowait()
        except queue.Empty:
            pass
        if "shutdown" in task_dict.keys() and task_dict["shutdown"]:
            break
        else:
            _update_task_dict(
                task_dict=task_dict,
                task_memory_dict=task_memory_dict,
                cache_directory=cache_directory,
            )


def read_from_file(file_name: str) -> dict:
    name = file_name.split("/")[-1].split(".")[0]
    with open(file_name, "rb") as f:
        return {name: f.read()}


def reload_previous_futures(
    future_queue: queue.Queue, future_dict: dict, cache_directory: str
):
    file_lst = os.listdir(cache_directory)
    for f in file_lst:
        if f.endswith(".in.pl"):
            key = f.split(".in.pl")[0]
            future_dict[key] = Future()
            file_name_out = key + ".out.pl"
            if file_name_out in file_lst:
                _set_future(
                    file_name=os.path.join(cache_directory, file_name_out),
                    future=future_dict[key],
                )
            else:
                future_queue.put({key: future_dict[key]})


def serialize_result(result_dict: dict):
    return {k: cloudpickle.dumps(v) for k, v in result_dict.items()}


def serialize_funct(fn: callable, *args, **kwargs):
    binary = cloudpickle.dumps({"fn": fn, "args": args, "kwargs": kwargs})
    return {fn.__name__ + _get_hash(binary=binary): binary}


def write_to_file(funct_dict: dict, state, cache_directory: str):
    file_name_lst = []
    for k, v in funct_dict.items():
        file_name = _get_file_name(name=k, state=state)
        file_name_lst.append(file_name)
        with open(os.path.join(cache_directory, file_name), "wb") as f:
            f.write(v)
    return file_name_lst


def _get_file_name(name, state):
    return name + "." + state + ".pl"


def _get_hash(binary):
    # Remove specification of jupyter kernel from hash to be deterministic
    binary_no_ipykernel = re.sub(b"(?<=/ipykernel_)(.*)(?=/)", b"", binary)
    return str(hashlib.md5(binary_no_ipykernel).hexdigest())


def _set_future(file_name, future):
    values = deserialize(funct_dict=read_from_file(file_name=file_name)).values()
    if len(values) == 1:
        future.set_result(list(values)[0])


def _update_task_dict(task_dict, task_memory_dict, cache_directory):
    file_lst = os.listdir(cache_directory)
    for key, future in task_dict.items():
        task_memory_dict[key] = future
    for key, future in task_memory_dict.items():
        file_name_out = _get_file_name(name=key, state="out")
        if not future.done() and file_name_out in file_lst:
            _set_future(
                file_name=os.path.join(cache_directory, file_name_out),
                future=future,
            )
