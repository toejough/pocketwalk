# coding: utf-8


"""Config help."""


# [ Imports ]
# [ -Python ]
from typing import Any
# [ -Third Party ]
import a_sync
import yaml
# [ -Project ]
from . import cli


# [ Helper Helpers ]
async def get_config(section: str) -> Any:
    """Return the config."""
    config_path = await cli.get_arg('config')
    try:
        return (await a_sync.run(yaml.load, config_path.read_text()))[section]
    except FileNotFoundError:
        exit(1)
