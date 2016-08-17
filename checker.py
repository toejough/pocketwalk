"""Check the files."""


# [ Imports ]
# [ -Python ]
import logging
from typing import Sequence, Callable
from pathlib import Path
# [ -Project ]
from runner import run
from command import Command


# [ Logging ]
logger = logging.getLogger(__name__)


# [ API ]
class Checker:
    """Checker."""

    def __init__(
        self, *,
        get_commands: Callable[[], Sequence[Command]],
        get_paths: Callable[[], Sequence[Path]],
        on_success: Callable[[], None]
    ) -> None:
        """Init the state."""
        self._get_commands = get_commands
        self._get_paths = get_paths
        self._on_success = on_success

    def run(self) -> None:
        """Run the checks."""
        logger.info("running the static checkers...")

        path_strings = tuple(str(p) for p in self._get_paths())

        for command in self._get_commands():
            args = command.args + path_strings
            result = run(command.command, args)
            if not result.success:
                return
        try:
            self._on_success()
        except Exception:
            logger.exception("Unexpected exception while running 'on_success' callback from checker.")
            exit(1)
