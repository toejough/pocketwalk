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
# XXX make logging level configurable
# XXX make logging location configurable
# XXX add unit tests
# [ Helpers ]
async def _get_watch_paths() -> Sequence[Path]:
    """Return the paths to watch."""
    check_paths = await _get_check_paths()
    config_path = await cli.get_arg('config')
    return [*check_paths, config_path]


async def _get_check_paths() -> Sequence[Path]:
    """Return the paths to check."""
    return [Path(p) for p in await config.get_config('paths')]


async def _get_commands() -> Sequence[Command]:
    """Return the commands to run."""
    return [Command(*c) for c in await config.get_config('checks')]


# [ Main ]
async def main() -> None:
    """Perform the static checking."""
    logger.info('Running static checker...')

    checker = Checker(
        get_commands=_get_commands,
        get_paths=_get_check_paths,
        on_success=commit
    )

    if await cli.get_arg('once'):
        await checker.run()
    else:
        await Watcher(
            get_paths=_get_watch_paths,
            on_modification=checker.run
        ).watch()


# satisfy vulture:
assert main
