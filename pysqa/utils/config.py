import yaml


def read_config(file_name: str = "queue.yaml") -> dict:
    """
    Read and parse a YAML configuration file.

    Args:
        file_name (str): The name of the YAML file to read.

    Returns:
        dict: The parsed configuration as a dictionary.
    """
    with open(file_name, "r") as f:
        return yaml.load(f, Loader=yaml.FullLoader)
