"""Watch files."""


# [ Imports ]
# [ -Python ]
import logging
from pprint import pformat
from typing import Sequence, Dict, Callable, Awaitable, Optional, Any
from pathlib import Path
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
    # XXX actually only get the changed paths - verify content changes before returning
    # XXX ^ will require a separate, special run the very first time (run all, regardless of changes)
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
        # XXX clarify and remove unnecessary Any types
        on_modification: Callable[[Any], Optional[Awaitable[None]]]
    ) -> None:
        """Init the state."""
        self._get_paths = get_paths
        self._unsafe_on_modification = on_modification

    async def _on_modification(self, changed_paths: Sequence[Path]) -> None:
        """Safe version of _unsafe_on_modification."""
        try:
            await a_sync.run(self._unsafe_on_modification, changed_paths)
        except concurrent.futures.CancelledError:
            logger.info("Run-checks cancelled.")
            raise
        except Exception:
            logger.exception("Unexpected exception while running 'on_modification' callback from watcher.")
            exit(1)

    async def watch(self) -> None:
        """Watch the paths."""
        last_mtimes = {}  # type: Dict[Path, float]
        running_checks = None
        # XXX way too complex
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
                    running_checks = asyncio.ensure_future(self._on_modification(changed_paths))  # type: ignore
                    last_mtimes = new_mtimes
                else:
                    silently = running_checks and not running_checks.done()
                    await _wait(silently=silently)
                    # await a_sync.run(_wait, silently=silently)
        except concurrent.futures.CancelledError:
            print("Stopped watching files.")
            raise
