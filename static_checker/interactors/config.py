"""Config help."""


# [ Imports ]
# [ -Python ]
import logging
from typing import Any
# [ -Third Party ]
import yaml
# [ -Project ]
from . import cli


# [ Logging ]
logger = logging.getLogger(__name__)


# XXX Better doc strings
# XXX rename get_config to just get
# XXX add unit tests
# [ Helper Helpers ]
def get_config(section: str) -> Any:
    """Return the config."""
    config_path = cli.get_arg('config')
    # XXX pull out just the unsafe stuff
    try:
        return yaml.load(config_path.read_text())[section]
    except FileNotFoundError:
        logger.critical(
            "The config file ({}) was not found.  Cannot continue.".format(
                str(config_path)
            ),
            stack_info=True
        )
        exit(1)
