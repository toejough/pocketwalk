#! /usr/bin/env python3
"""Static checking."""


# [ Imports ]
# [ -Python ]
from pathlib import Path
import logging
from typing import Sequence, Any
# [ -Third Party ]
import yaml
# [ -Project ]
from checker import Checker
from watcher import Watcher
from runner import run
from command import Command


# [ Global ]
CONFIG_PATH = Path(__name__).parent / 'check.yaml'


# [ Logging ]
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# [ Helper Helpers ]
def get_config(section: str) -> Any:
    """Return the config."""
    return yaml.load(CONFIG_PATH.read_text())[section]


# [ Helpers ]
def get_paths() -> Sequence[Path]:
    """Return the paths to watch/check."""
    return [Path(p) for p in get_config('paths')]


def get_commands() -> Sequence[Command]:
    """Return the commands to run."""
    return [Command(*c) for c in get_config('checks')]


def commit() -> None:
    """Commit the current repo."""
    logger.info('committing...')
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

    Watcher(
        get_paths=get_paths,
        on_modification=checker.run
    ).watch()


if __name__ == "__main__":
    main()
