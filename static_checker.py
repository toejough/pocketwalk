#! /usr/bin/env python3
"""Static checking."""


# [ Imports ]
# [ -Python ]
from pathlib import Path
import logging
# [ -Project ]
from checker import Checker
from watcher import Watcher
from runner import run


# [ Logging ]
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# [ Helpers ]
def get_paths():
    """Return the paths to watch/check."""
    return [
        Path(__file__),
        Path(__file__).parent / 'runner.py',
        Path(__file__).parent / 'checker.py',
        Path(__file__).parent / 'watcher.py',
    ]


def get_commands():
    """Return the commands to run."""
    return [
        'vulture',
        'prospector',
        ['mypy', '--fast-parser', '--disallow-untyped-defs'],
    ]


def commit():
    """Commit the current repo."""
    logger.info('committing...')
    run('git', ['commit', '-am', "static checks passed"])


# [ Main ]
def main():
    """Perform the static checking."""
    logger.info('Running static checker...')

    paths = get_paths()
    commands = get_commands()

    checker = Checker(
        commands=commands,
        paths=paths,
        on_success=commit
    )

    Watcher(
        paths=paths,
        on_modification=checker.run
    ).watch()


if __name__ == "__main__":
    main()
