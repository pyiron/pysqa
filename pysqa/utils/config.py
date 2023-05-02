import yaml


def read_config(file_name="queue.yaml"):
    """

    Args:
        file_name (str):

    Returns:
        dict:
    """
    with open(file_name, "r") as f:
        return yaml.load(f, Loader=yaml.FullLoader)
