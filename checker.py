"""Check the files."""


# [ Imports ]
from runner import run
import logging


# [ Logging ]
logger = logging.getLogger(__name__)


# [ API ]
class Checker:
    """Checker."""

    def __init__(self, *, commands, paths, on_success):
        """Init the state."""
        self._commands = commands
        self._paths = paths
        self._on_success = on_success

    def run(self):
        """Run the checks."""
        logger.info("running the static checkers...")

        path_strings = [str(p) for p in self._paths]

        for command in self._commands:
            result = run(command, path_strings)
            if not result.success:
                return
        try:
            self._on_success()
        except Exception:
            logger.exception("Unexpected exception while running 'on_success' callback from checker.")
            exit(1)
