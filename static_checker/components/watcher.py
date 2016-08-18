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
# XXX print the file being checked
# XXX show what files changed
# XXX Async for blocking calls
# XXX checks are sagas
# XXX add unit tests
def get_mtimes(paths: Sequence[Path]) -> Dict[Path, int]:
    """Return the mtimes for the paths."""
    logger.debug("getting mtimes for {}".format(pformat(paths)))

    mtimes = {}
    for p in paths:
        try:
            mtimes[p] = p.stat().st_mtime
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

    def _watch(self, paths: Sequence[Path]) -> None:
        """Watch the paths."""
        last_mtimes = None
        while True:
            new_mtimes = get_mtimes(paths)
            if last_mtimes != new_mtimes:
                print("\rFound changes...{}".format(T.clear_eol))
                self._on_modification()
                last_mtimes = new_mtimes
            else:
                _wait()

    def _interruptable_watch(self, paths: Sequence[Path]) -> None:
        """Watch, interruptable by Ctrl-c."""
        try:
            self._watch(paths)
        except KeyboardInterrupt:
            print("\nReceived Ctrl-c.  Stopping.")
            exit(0)

    def watch(self) -> None:
        """Watch the files."""
        paths = self._get_paths()
        logger.info("watching {}".format(pformat(paths)))

        self._interruptable_watch(paths)
