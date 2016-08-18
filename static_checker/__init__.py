"""Static checking."""


# [ Imports ]
# [ -Python ]
from pathlib import Path
import logging
from typing import Sequence
# [ -Project ]
from .components.checker import Checker
from .components.watcher import Watcher
from .components.source_control import commit
from .interactors import config
from .interactors import cli
from .thin_types.command import Command


# [ Logging ]
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


# XXX Better doc strings
# XXX watch the config file by default
# XXX add unit tests
# [ Helpers ]
def get_paths() -> Sequence[Path]:
    """Return the paths to watch/check."""
    # XXX rename get_config to just get
    return [Path(p) for p in config.get_config('paths')]


def get_commands() -> Sequence[Command]:
    """Return the commands to run."""
    return [Command(*c) for c in config.get_config('checks')]


# [ Main ]
def main() -> None:
    """Perform the static checking."""
    logger.info('Running static checker...')

    checker = Checker(
        get_commands=get_commands,
        get_paths=get_paths,
        on_success=commit
    )

    if cli.get_arg('once'):
        checker.run()
    else:
        Watcher(
            get_paths=get_paths,
            on_modification=checker.run
        ).watch()


# satisfy vulture:
assert main
