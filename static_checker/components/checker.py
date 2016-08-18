"""Check the files."""


# [ Imports ]
# [ -Python ]
import logging
from typing import Sequence, Callable
from pathlib import Path
import sys
# [ -Project ]
from ..interactors.runner import run
from ..thin_types.command import Command


# [ Logging ]
logger = logging.getLogger(__name__)


# [ API ]
# XXX Better doc strings
# XXX add unit tests
class Checker:
    """Checker."""

    def __init__(
        self, *,
        get_commands: Callable[[], Sequence[Command]],
        get_paths: Callable[[], Sequence[Path]],
        on_success: Callable[[Sequence[Path]], None]
    ) -> None:
        """Init the state."""
        self._get_commands = get_commands
        self._get_paths = get_paths
        self._unsafe_on_success = on_success

    def _on_success(self, paths: Sequence[Path]) -> None:
        """Run the passed in 'on_success' function safely."""
        try:
            self._unsafe_on_success(paths)
        except Exception:
            logger.exception("Unexpected exception while running 'on_success' callback from checker.")
            exit(1)

    def run(self) -> None:
        """Run the checks."""
        logger.info("running the static checkers...")

        paths = self._get_paths()
        path_strings = tuple(str(p) for p in paths)

        for command in self._get_commands():
            # XXX status output
            # XXX colored check/x
            # XXX bold current command
            # XXX normal old command
            args = command.args + path_strings
            print("running {}...".format(command.command), end='')
            sys.stdout.flush()
            result = run(command.command, args)
            report_result = 'pass' if result.success else 'fail'
            print(report_result)
            if not result.success:
                print("{} output:".format(command.command))
                print(result.output)
                return

        self._on_success(paths)
