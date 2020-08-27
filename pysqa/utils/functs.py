import yaml
from pysqa.utils.basic import BasisQueueAdapter
from pysqa.utils.remote import RemoteQueueAdapter
from pysqa.utils.modular import ModularQueueAdapter


def read_config(file_name="queue.yaml"):
    """

    Args:
        file_name (str):

    Returns:
        dict:
    """
    with open(file_name, "r") as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def set_queue_adapter(config, directory):
    """
    Initialize the queue adapter

    Args:
        config (dict): configuration for one cluster
        directory (str): directory which contains the queue configurations
    """
    if config["queue_type"] in ["SGE", "TORQUE", "SLURM", "LSF", "MOAB"]:
        return BasisQueueAdapter(config=config, directory=directory)
    elif config["queue_type"] in ["GENT"]:
        return ModularQueueAdapter(config=config, directory=directory)
    elif config["queue_type"] in ["REMOTE"]:
        return RemoteQueueAdapter(config=config, directory=directory)
    else:
        raise ValueError
