from pydantic import BaseModel, ConfigDict


class QueueModel(BaseModel):
    """
    Pydantic model for a single queue configuration.
    """

    model_config = ConfigDict(extra="allow")

    script: str | None = None
    cores_min: int | None = None
    cores_max: int | None = None
    run_time_max: int | None = None
    memory_max: int | str | None = None


class ConfigModel(BaseModel):
    """
    Pydantic model for the overall configuration.
    """

    model_config = ConfigDict(extra="allow")

    queue_type: str
    queue_primary: str | None = None
    ssh_host: str | None = None
    ssh_username: str | None = None
    known_hosts: str | None = None
    ssh_key: str | None = None
    ssh_password: str | None = None
    ssh_ask_for_password: str | None = None
    ssh_key_passphrase: str | None = None
    ssh_two_factor_authentication: bool = False
    ssh_authenticator_service: str | None = None
    ssh_proxy_host: str | None = None
    ssh_remote_config_dir: str | None = None
    ssh_remote_path: str | None = None
    ssh_local_path: str | None = None
    ssh_port: int | None = None
    ssh_continous_connection: bool = False
    ssh_delete_file_on_remote: bool = True
    python_executable: str | None = None
    queues: dict[str, QueueModel]


def validate_config(config: dict) -> dict:
    """
    Validate the configuration dictionary against the ConfigModel.

    Args:
        config (dict): The configuration dictionary to validate.

    Returns:
        dict: The validated configuration dictionary.
    """
    return ConfigModel(**config).model_dump(exclude_none=True, exclude_defaults=True)
