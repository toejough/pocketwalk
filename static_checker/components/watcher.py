"""Watch files."""


# [ Imports ]
# [ -Python ]
import logging
from pprint import pformat
from typing import Sequence, Dict, Callable, Awaitable, Optional
from pathlib import Path
from time import sleep
import asyncio
import concurrent.futures
# [ -Third Party ]
import blessed
import a_sync


# [ Terminal ]
T = blessed.Terminal()


# [ Logging ]
logger = logging.getLogger(__name__)


# [ Helpers ]
# XXX Better doc strings
# XXX add unit tests
async def _get_mtimes(paths: Sequence[Path]) -> Dict[Path, float]:
    """Return the mtimes for the paths."""
    logger.debug("getting mtimes for {}".format(pformat(paths)))

    mtimes = {}
    for p in paths:
        try:
            stats = await a_sync.run(p.stat)
            mtimes[p] = stats.st_mtime
        except FileNotFoundError:
            # Try again?
            # fail out if not found a second time.
            await asyncio.sleep(0.1)
            stats = await a_sync.run(p.stat)
            mtimes[p] = stats.st_mtime
    return mtimes


async def _wait(*, silently: bool) -> None:
    """Wait."""
    if not silently:
        print("\rWaiting for changes...{}".format(
            T.clear_eol
        ), end='')
    await asyncio.sleep(1)


def _get_changed_paths(last_mtimes: Dict[Path, float], new_mtimes: Dict[Path, float]) -> Sequence[Path]:
    """Get the changed paths."""
    new_paths = [k for k in new_mtimes if k not in last_mtimes]
    maintained_paths = [k for k in last_mtimes if k in new_mtimes]
    modified_paths = [p for p in maintained_paths if new_mtimes[p] != last_mtimes[p]]
    removed_paths = [k for k in last_mtimes if k not in new_mtimes]
    return new_paths + modified_paths + removed_paths


# [ API ]
class Watcher:
    """Watch files."""

    def __init__(
        self, *,
        get_paths: Callable[[], Awaitable[Sequence[Path]]],
        on_modification: Callable[[], Optional[Awaitable[None]]]
    ) -> None:
        """Init the state."""
        self._get_paths = get_paths
        self._unsafe_on_modification = on_modification

    async def _on_modification(self) -> None:
        """Safe version of _unsafe_on_modification."""
        try:
            await a_sync.run(self._unsafe_on_modification)
        except concurrent.futures.CancelledError:
            logger.info("Run-checks cancelled.")
            raise
        except Exception:
            logger.exception("Unexpected exception while running 'on_modification' callback from watcher.")
            exit(1)

    async def _watch(self) -> None:
        """Watch the paths."""
        last_mtimes = {}  # type: Dict[Path, float]
        running_checks = None
        try:
            while True:
                paths = await self._get_paths()
                new_mtimes = await _get_mtimes(paths)
                changed_paths = _get_changed_paths(last_mtimes, new_mtimes)
                if changed_paths:
                    print("\rFound changes in files:{}\n{}".format(
                        T.clear_eol,
                        pformat([str(p) for p in changed_paths])
                    ))
                    if running_checks:
                        if running_checks.cancel():
                            print("Cancelled running checks due to mid-check changes.")
                    # XXX mypy says ensure_future is not a thing
                    running_checks = asyncio.ensure_future(self._on_modification())  # type: ignore
                    last_mtimes = new_mtimes
                else:
                    if running_checks and running_checks.done():
                        e = running_checks.exception()
                        if e:
                            raise e
                    # XXX cancel running check here if cancelled?
                    silently = running_checks and not running_checks.done()
                    await _wait(silently=silently)
                    # await a_sync.run(_wait, silently=silently)
        except (concurrent.futures.CancelledError, KeyboardInterrupt):
            if running_checks:
                print("running check cancelled")
                running_checks.cancel()
                asyncio.wait_for(running_checks, timeout=None)
            raise

    async def _interruptable_watch(self) -> None:
        """Watch, interruptable by Ctrl-c."""
        try:
            await self._watch()
        # XXX figure out keyboard interrupt for async - gives nasty bt
        except KeyboardInterrupt:
            # no async around this - we're exiting.
            print("\nReceived Ctrl-c.  Stopping.")
            exit(0)

    async def watch(self) -> None:
        """Watch the files."""
        await self._interruptable_watch()
