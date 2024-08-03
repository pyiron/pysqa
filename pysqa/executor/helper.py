import hashlib
import os
import queue
import re
from concurrent.futures import Future

import cloudpickle


def deserialize(funct_dict: dict) -> dict:
    """
    Deserialize a dictionary of serialized functions.

    Args:
        funct_dict (dict): A dictionary containing serialized functions.

    Returns:
        dict: A dictionary with deserialized functions.

    """
    try:
        return {k: cloudpickle.loads(v) for k, v in funct_dict.items()}
    except EOFError:
        return {}


def find_executed_tasks(future_queue: queue.Queue, cache_directory: str) -> None:
    """
    Find executed tasks from the future queue and update the task memory dictionary.

    Args:
        future_queue (queue.Queue): The queue containing the futures of executed tasks.
        cache_directory (str): The directory where the task cache is stored.

    Returns:
        None

    """
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
    """
    Read the contents of a file and return it as a dictionary.

    Args:
        file_name (str): The name of the file to read.

    Returns:
        dict: A dictionary containing the contents of the file, with the file name as the key.

    """
    name = file_name.split("/")[-1].split(".")[0]
    with open(file_name, "rb") as f:
        return {name: f.read()}


def reload_previous_futures(
    future_queue: queue.Queue, future_dict: dict, cache_directory: str
) -> None:
    """
    Reload previous futures from the cache directory and update the future dictionary.

    Args:
        future_queue (queue.Queue): The queue containing the futures of executed tasks.
        future_dict (dict): A dictionary containing the current futures.
        cache_directory (str): The directory where the task cache is stored.

    Returns:
        None

    """
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


def serialize_result(result_dict: dict) -> dict:
    """
    Serialize the values in a dictionary using cloudpickle.

    Args:
        result_dict (dict): A dictionary containing the values to be serialized.

    Returns:
        dict: A dictionary with serialized values.

    """
    return {k: cloudpickle.dumps(v) for k, v in result_dict.items()}


def serialize_funct(fn: callable, *args, **kwargs) -> dict:
    """
    Serialize a function along with its arguments and keyword arguments.

    Args:
        fn (callable): The function to be serialized.
        *args: The arguments to be passed to the function.
        **kwargs: The keyword arguments to be passed to the function.

    Returns:
        dict: A dictionary containing the serialized function.

    """
    binary = cloudpickle.dumps({"fn": fn, "args": args, "kwargs": kwargs})
    return {fn.__name__ + _get_hash(binary=binary): binary}


def write_to_file(funct_dict: dict, state: str, cache_directory: str) -> List[str]:
    """
    Write the contents of a dictionary to files in the cache directory.

    Args:
        funct_dict (dict): A dictionary containing the contents to be written.
        state (str): The state of the files to be written.
        cache_directory (str): The directory where the files will be written.

    Returns:
        List[str]: A list of file names that were written.

    """
    file_name_lst = []
    for k, v in funct_dict.items():
        file_name = _get_file_name(name=k, state=state)
        file_name_lst.append(file_name)
        with open(os.path.join(cache_directory, file_name), "wb") as f:
            f.write(v)
    return file_name_lst


def _get_file_name(name: str, state: str) -> str:
    """
    Generate a file name based on the given name and state.

    Args:
        name (str): The name to be included in the file name.
        state (str): The state of the file.

    Returns:
        str: The generated file name.

    """
    return name + "." + state + ".pl"


def _get_hash(binary: bytes) -> str:
    """
    Get the hash of a binary using MD5 algorithm.

    Args:
        binary (bytes): The binary data to be hashed.

    Returns:
        str: The hexadecimal representation of the hash.

    """
    # Remove specification of jupyter kernel from hash to be deterministic
    binary_no_ipykernel = re.sub(b"(?<=/ipykernel_)(.*)(?=/)", b"", binary)
    return str(hashlib.md5(binary_no_ipykernel).hexdigest())


def _set_future(file_name: str, future: Future) -> None:
    """
    Set the result of a future based on the contents of a file.

    Args:
        file_name (str): The name of the file containing the result.
        future (Future): The future to set the result for.

    Returns:
        None

    """
    values = deserialize(funct_dict=read_from_file(file_name=file_name)).values()
    if len(values) == 1:
        future.set_result(list(values)[0])


def _update_task_dict(
    task_dict: dict, task_memory_dict: dict, cache_directory: str
) -> None:
    """
    Update the task memory dictionary with the futures from the task dictionary.

    Args:
        task_dict (dict): A dictionary containing the futures of tasks.
        task_memory_dict (dict): The dictionary to store the task memory.
        cache_directory (str): The directory where the task cache is stored.

    Returns:
        None

    """
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
