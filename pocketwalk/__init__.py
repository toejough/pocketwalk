"""Static checking."""
# coding: utf-8


# [ Imports ]
# [ -Python ]
import asyncio
import concurrent.futures
# mypy drops some error about where glob is defined?
import glob  # type: ignore
import itertools
import signal
from pathlib import Path
from typing import Sequence
# [ -Third Party ]
import a_sync
# [ -Project ]
from .components.checker import Checker
from .components.source_control import commit
from .components.watcher import Watcher
from .interactors import cli
from .interactors import config
from .thin_types.command import Command


# [ Helpers ]
async def _get_watch_paths() -> Sequence[Path]:
    """Return the paths to watch."""
    check_paths = await _get_check_paths()
    config_path = await cli.get_arg('config')
    return [*check_paths, config_path]


async def _get_check_paths() -> Sequence[Path]:
    """Return the paths to check."""
    path_strings = await config.get_config('paths')
    unglobbed_path_strings = []
    for this_path_string in path_strings:
        # mypy says no 'recursive' arg for glob.
        unglobbed_path_list = glob.glob(this_path_string, recursive=True)  # type: ignore
        unglobbed_path_strings.append(unglobbed_path_list)
    flattened_path_strings = itertools.chain(*unglobbed_path_strings)
    paths = [Path(p) for p in flattened_path_strings]
    return paths


async def _get_commands() -> Sequence[Command]:
    """Return the commands to run."""
    return [Command(*c) for c in await config.get_config('checks')]


async def _check(checker: Checker) -> None:
    """Check the files."""
    if await cli.get_arg('once'):
        await checker.run(_get_watch_paths())
    else:
        await Watcher(
            get_paths=_get_watch_paths,
            on_modification=checker.run,
        ).watch()


def handler() -> None:
    """Handle SIGINT by cancelling everything."""
    print('\nCaught Ctrl-c.')
    all_tasks = list(asyncio.Task.all_tasks())
    pending_tasks = [t for t in all_tasks if not t.done()]
    if pending_tasks:
        print('Winding down...')
        for task in pending_tasks:
            task.cancel()


async def _unfriendly_main() -> None:
    """Not ctrl-c-friendly."""
    checker = Checker(
        get_commands=_get_commands,
        get_paths=_get_check_paths,
        on_success=commit,
    )

    await _check(checker)


# [ Main ]
def main() -> None:
    """Interruptable main func."""
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, handler)
    try:
        a_sync.block(_unfriendly_main)
    except concurrent.futures.CancelledError:
        pass
    finally:
        all_tasks = list(asyncio.Task.all_tasks())
        pending_tasks = [t for t in all_tasks if not t.done()]
        loop = asyncio.get_event_loop()
        if pending_tasks:
            loop.run_until_complete(asyncio.wait(pending_tasks))
        loop.close()
        print("Done.")


# satisfy vulture:
assert main
