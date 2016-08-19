"""Source Control."""


# [ Imports ]
# [ -Python ]
from pathlib import Path
import logging
from typing import Sequence
import concurrent.futures
# [ -Third Party ]
import a_sync
# [ -Project ]
from ..interactors.runner import run


# [ Logging ]
logger = logging.getLogger(__name__)


# XXX Better doc strings
# XXX add unit tests
# [ Helpers ]
async def _get_status() -> Sequence[str]:
    """Get repo status."""
    logger.info('getting status...')
    return (await run('git', ['status', '--porcelain'])).output.splitlines()


async def _add_missing_paths(paths: Sequence[Path], status_lines: Sequence[str]) -> None:
    """Add any missing paths to the repo."""
    logger.info('adding missing paths...')
    if not status_lines:
        return
    new_file_lines = [l for l in status_lines if l.startswith('??')]
    new_path_strings = [v for l in new_file_lines for k, v in [l.split()]]
    for path in paths:
        path_string = str(path)
        if path_string in new_path_strings:
            await run('git', ['add', path_string])


# [ API ]
async def commit(paths: Sequence[Path]) -> None:
    """Commit the current repo."""
    logger.info('committing...')
    status_lines = await _get_status()
    await _add_missing_paths(paths, status_lines)
    modified_file_lines = [l for l in status_lines if not l.startswith('??')]
    if not modified_file_lines:
        return
    print((await run('git', ['diff', '--color'])).output)
    try:
        message = await a_sync.run(input, 'commit message: ')
    except concurrent.futures.CancelledError:
        raise
    await run('git', ['commit', '-am', message])
