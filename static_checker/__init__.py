"""Static checking."""


# [ Imports ]
# [ -Python ]
from pathlib import Path
import logging
from typing import Sequence
# [ -Project ]
from .components.checker import Checker
from .components.watcher import Watcher
from .interactors.runner import run
from .thin_types.command import Command
from .interactors import config
from .interactors import cli


# [ Logging ]
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# XXX Better doc strings
# XXX prompt the user for their commit message
# XXX show user actual changes
# XXX print the file being checked
# XXX Bump logging to warning
# XXX add unit tests
# [ Helpers ]
def get_paths() -> Sequence[Path]:
    """Return the paths to watch/check."""
    # XXX rename get_config to just get
    return [Path(p) for p in config.get_config('paths')]


def get_commands() -> Sequence[Command]:
    """Return the commands to run."""
    return [Command(*c) for c in config.get_config('checks')]


def commit(paths: Sequence[Path]) -> None:
    """Commit the current repo."""
    logger.info('committing...')
    for path in paths:
        run('git', ['add', str(path)])
    run('git', ['commit', '-am', "static checks passed"])


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
