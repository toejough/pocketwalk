"""Watch files."""


# [ Imports ]
import logging
from pprint import pformat


# [ Logging ]
logger = logging.getLogger(__name__)


# [ Helpers ]
def get_mtimes(paths):
    """Return the mtimes for the paths."""
    logger.debug("getting mtimes for {}".format(pformat(paths)))

    mtimes = {}
    for p in paths:
        mtimes[p] = p.stat().st_mtime
    return mtimes


# [ API ]
class Watcher:
    """Watch files."""

    def __init__(self, *, paths, on_modification):
        """Init the state."""
        self._paths = paths
        self._on_modification = on_modification

    def watch(self):
        """Watch the files."""
        logger.info("watching {}".format(pformat(self._paths)))

        last_mtimes = None
        try:
            while True:
                new_mtimes = get_mtimes(self._paths)
                if last_mtimes != new_mtimes:
                    try:
                        self._on_modification()
                    except Exception:
                        logger.exception("Unexpected exception while running 'on_modification' callback from watcher.")
                        exit(1)
                    last_mtimes = new_mtimes
        except KeyboardInterrupt:
            print("\nReceived Ctrl-c.  Stopping.")
            exit(0)
