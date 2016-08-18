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
    status_lines = run('git', ['status', '--porcelain']).output.splitlines()
    if not status_lines:
        return
    new_file_lines = [l for l in status_lines if l.startswith('??')]
    new_path_strings = [v for l in new_file_lines for k, v in [l.split()]]
    for path in paths:
        path_string = str(path)
        if path_string in new_path_strings:
            run('git', ['add', path_string])
    if new_path_strings:
        status_lines = run('git', ['status', '--porcelain']).output.splitlines()
        if not status_lines:
            return
    modified_file_lines = [l for l in status_lines if not l.startswith('??')]
    if not modified_file_lines:
        return
    print(run('git', ['diff', '--color']).output)
    message = input('commit message: ')
    run('git', ['commit', '-am', message])


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
