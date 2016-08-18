"""Watch files."""


# [ Imports ]
# [ -Python ]
import logging
from pprint import pformat
from typing import Sequence, Dict, Callable
from pathlib import Path
from time import sleep
import sys
# [ -Third Party ]
import blessed


# [ Terminal ]
T = blessed.Terminal()


# [ Logging ]
logger = logging.getLogger(__name__)


# [ Helpers ]
# XXX Better doc strings
# XXX Async for blocking calls
# XXX checks are sagas
# XXX add unit tests
def _get_mtimes(paths: Sequence[Path]) -> Dict[Path, float]:
    """Return the mtimes for the paths."""
    logger.debug("getting mtimes for {}".format(pformat(paths)))

    mtimes = {}
    for p in paths:
        try:
            stats = p.stat()
            mtimes[p] = stats.st_mtime
        except FileNotFoundError:
            # Try again?
            # fail out if not found a second time.
            sleep(0.1)
            mtimes[p] = p.stat().st_mtime
    return mtimes


def _wait() -> None:
    """Wait."""
    print("\rWaiting for changes...{}".format(
        T.clear_eol
    ), end='')
    sys.stdout.flush()
    sleep(1)


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
        get_paths: Callable[[], Sequence[Path]],
        on_modification: Callable[[], None]
    ) -> None:
        """Init the state."""
        self._get_paths = get_paths
        self._unsafe_on_modification = on_modification

    def _on_modification(self) -> None:
        """Safe version of _unsafe_on_modification."""
        try:
            self._unsafe_on_modification()
        except Exception:
            logger.exception("Unexpected exception while running 'on_modification' callback from watcher.")
            exit(1)

    def _watch(self) -> None:
        """Watch the paths."""
        last_mtimes = {}  # type: Dict[Path, float]
        while True:
            paths = self._get_paths()
            new_mtimes = _get_mtimes(paths)
            changed_paths = _get_changed_paths(last_mtimes, new_mtimes)
            if changed_paths:
                print("\rFound changes in files:{}\n{}".format(
                    T.clear_eol,
                    pformat([str(p) for p in changed_paths])
                ))
                self._on_modification()
                last_mtimes = new_mtimes
            else:
                _wait()

    def _interruptable_watch(self) -> None:
        """Watch, interruptable by Ctrl-c."""
        try:
            self._watch()
        except KeyboardInterrupt:
            print("\nReceived Ctrl-c.  Stopping.")
            exit(0)

    def watch(self) -> None:
        """Watch the files."""
        self._interruptable_watch()
