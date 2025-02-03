import re
from typing import Optional, Union


def check_queue_parameters(
    active_queue: Optional[dict] = None,
    cores: int = 1,
    run_time_max: Optional[int] = None,
    memory_max: Optional[int] = None,
) -> tuple[Union[float, int, None], Union[float, int, None], Union[float, int, None]]:
    """
    Check the parameters of a queue.

    Args:

        cores (int, optional): The number of cores. Defaults to 1.
        run_time_max (int, optional): The maximum run time. Defaults to None.
        memory_max (int, optional): The maximum memory. Defaults to None.
        active_queue (dict, optional): The active queue. Defaults to None.

    Returns:
        list: A list of queue parameters [cores, run_time_max, memory_max].
    """
    cores = value_in_range(
        value=cores,
        value_min=active_queue["cores_min"],
        value_max=active_queue["cores_max"],
    )
    run_time_max = value_in_range(
        value=run_time_max, value_max=active_queue["run_time_max"]
    )
    memory_max = value_in_range(value=memory_max, value_max=active_queue["memory_max"])
    return cores, run_time_max, memory_max


def value_error_if_none(value: str) -> None:
    """
    Raise a ValueError if the value is None or not a string.

    Args:
        value (str/None): The value to check.

    Raises:
        ValueError: If the value is None.
        TypeError: If the value is not a string.
    """
    if value is None:
        raise ValueError("Value cannot be None.")
    if not isinstance(value, str):
        raise TypeError()


def value_in_range(
    value: Union[int, float, None],
    value_min: Union[int, float, None] = None,
    value_max: Union[int, float, None] = None,
) -> Union[int, float, None]:
    """
    Check if a value is within a specified range.

    Args:
        value (int/float/None): The value to check.
        value_min (int/float/None): The minimum value. Defaults to None.
        value_max (int/float/None): The maximum value. Defaults to None.

    Returns:
        int/float/None: The value if it is within the range, otherwise the minimum or maximum value.
    """

    if value is not None:
        value_, value_min_, value_max_ = [
            (
                _memory_spec_string_to_value(v)
                if v is not None and isinstance(v, str)
                else v
            )
            for v in (value, value_min, value_max)
        ]
        # ATTENTION: '60000' is interpreted as '60000M' since default magnitude is 'M'
        # ATTENTION: int('60000') is interpreted as '60000B' since _memory_spec_string_to_value return the size in
        # ATTENTION: bytes, as target_magnitude = 'b'
        # We want to compare the the actual (k,m,g)byte value if there is any
        if value_min_ is not None and value_ < value_min_:
            return value_min
        if value_max_ is not None and value_ > value_max_:
            return value_max
        return value
    else:
        if value_min is not None:
            return value_min
        if value_max is not None:
            return value_max
        return value


def _is_memory_string(value: str) -> bool:
    """
    Check if a string specifies a certain amount of memory.

    Args:
        value (str): The string to check.

    Returns:
        bool: True if the string matches a memory specification, False otherwise.
    """
    memory_spec_pattern = r"[0-9]+[bBkKmMgGtT]?"
    return re.findall(memory_spec_pattern, value)[0] == value


def _memory_spec_string_to_value(
    value: Union[str, int, float],
    default_magnitude: str = "m",
    target_magnitude: str = "b",
) -> Union[int, float]:
    """
    Converts a valid memory string (tested by _is_memory_string) into an integer/float value of desired
    magnitude `default_magnitude`. If it is a plain integer string (e.g.: '50000') it will be interpreted with
    the magnitude passed in by the `default_magnitude`. The output will rescaled to `target_magnitude`

    Args:
        value (str): The string to convert.
        default_magnitude (str): The magnitude for interpreting plain integer strings [b, B, k, K, m, M, g, G, t, T]. Defaults to "m".
        target_magnitude (str): The magnitude to which the output value should be converted [b, B, k, K, m, M, g, G, t, T]. Defaults to "b".

    Returns:
        Union[int, float]: The value of the string in `target_magnitude` units.
    """
    magnitude_mapping = {"b": 0, "k": 1, "m": 2, "g": 3, "t": 4}
    if _is_memory_string(value):
        integer_pattern = r"[0-9]+"
        magnitude_pattern = r"[bBkKmMgGtT]+"
        integer_value = int(re.findall(integer_pattern, value)[0])

        magnitude = re.findall(magnitude_pattern, value)
        if len(magnitude) > 0:
            magnitude = magnitude[0].lower()
        else:
            magnitude = default_magnitude.lower()
        # Convert it to default magnitude = megabytes
        return (integer_value * 1024 ** magnitude_mapping[magnitude]) / (
            1024 ** magnitude_mapping[target_magnitude]
        )
    else:
        return value
