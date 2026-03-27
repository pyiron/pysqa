from typing import Optional, Union

from pydantic import BaseModel, ConfigDict


class QueueModel(BaseModel):
    """
    Pydantic model for a single queue configuration.
    """

    model_config = ConfigDict(extra="allow")

    script: Optional[str] = None
    cores_min: Optional[int] = None
    cores_max: Optional[int] = None
    run_time_max: Optional[int] = None
    memory_max: Optional[Union[int, str]] = None


class ConfigModel(BaseModel):
    """
    Pydantic model for the overall configuration.
    """

    model_config = ConfigDict(extra="allow")

    queue_type: str
    queue_primary: Optional[str] = None
    ssh_host: Optional[str] = None
    ssh_username: Optional[str] = None
    known_hosts: Optional[str] = None
    ssh_key: Optional[str] = None
    ssh_remote_config_dir: Optional[str] = None
    ssh_remote_path: Optional[str] = None
    ssh_local_path: Optional[str] = None
    ssh_continous_connection: bool = True
    ssh_delete_file_on_remote: bool = False
    queues: dict[str, QueueModel]


def validate_config(config: dict) -> dict:
    """
    Validate the configuration dictionary against the ConfigModel.

    Args:
        config (dict): The configuration dictionary to validate.

    Returns:
        dict: The validated configuration dictionary.
    """
    return ConfigModel(**config).model_dump()
