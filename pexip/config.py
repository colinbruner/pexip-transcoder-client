import os
import json
import errno

from pathlib import Path
from typing import Union

DEFAULT_RELATIVE_CONFIG_HOME = Path(".pexip")

ENV_PEXIP_CONFIG_DIR = "PEXIP_CONFIG_DIR"


def get_default_config_dir() -> Path:
    """
    Find the default Pexip config directory.
    """

    # 1. Grab through Env
    env_config_dir = os.environ.get(ENV_PEXIP_CONFIG_DIR)
    if env_config_dir:
        return Path(env_config_dir)

    # 2 Check local directory to see if .pexip/ exists
    local_config_dir = Path.cwd() / DEFAULT_RELATIVE_CONFIG_HOME
    if local_config_dir.exists():
        return local_config_dir

    # 3 Check home directory to see if .pexip/ exists
    home_config_dir = Path.home() / DEFAULT_RELATIVE_CONFIG_HOME
    if home_config_dir.exists():
        return home_config_dir


DEFAULT_CONFIG_DIR = get_default_config_dir()


class ConfigFileError(Exception):
    pass


class BaseConfigDict(dict):
    name = None
    helpurl = None
    about = None

    def __init__(self, path: Path):
        super().__init__()
        self.path = path


class Config(BaseConfigDict):
    FILENAME = "config.json"

    def __init__(self, directory=DEFAULT_CONFIG_DIR):
        # if a directory isn't found, just return
        if not directory:
            return 

        self.directory = Path(directory)
        super().__init__(path=self.directory / self.FILENAME)
        try:
            with self.path.open("rt") as f:
                try:
                    data = json.load(f)
                except ValueError as e:
                    data = {}
        except IOError as e:
            data = {}

        self.update(data)
