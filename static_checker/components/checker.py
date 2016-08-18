"""Check the files."""


# [ Imports ]
# [ -Python ]
import logging
from typing import Sequence, Callable, Awaitable
from pathlib import Path
import sys
from types import SimpleNamespace
# [ -Third Party ]
import a_sync
# [ -Project ]
from ..interactors.runner import run
from ..thin_types.command import Command


# [ Logging ]
logger = logging.getLogger(__name__)


# [ Helpers ]
def report_part(part: str) -> None:
    """Report some partial data (no newline)."""
    print(part, end='')
    sys.stdout.flush()


def report_result(command: str, result: SimpleNamespace) -> None:
    """Report the result."""
    outcome = 'pass' if result.success else 'fail'
    print(outcome)
    if not result.success:
        print("{} output:".format(command))
        print(result.output)


# [ API ]
# XXX Better doc strings
# XXX add unit tests
class Checker:
    """Checker."""

    def __init__(
        self, *,
        get_commands: Callable[[], Awaitable[Sequence[Command]]],
        get_paths: Callable[[], Awaitable[Sequence[Path]]],
        on_success: Callable[[Sequence[Path]], Awaitable[None]]
    ) -> None:
        """Init the state."""
        self._get_commands = get_commands
        self._get_paths = get_paths
        self._unsafe_on_success = on_success

    async def _on_success(self, paths: Sequence[Path]) -> None:
        """Run the passed in 'on_success' function safely."""
        try:
            await a_sync.run(self._unsafe_on_success, paths)
        except Exception:
            logger.exception("Unexpected exception while running 'on_success' callback from checker.")
            exit(1)

    # XXX only check changed files for prospector
    async def run(self) -> None:
        """Run the checks."""
        logger.info("running the static checkers...")

        paths = await self._get_paths()
        path_strings = tuple(str(p) for p in paths)

        for command in await self._get_commands():
            # XXX colored check/x
            # XXX bold current command
            # XXX normal old command
            args = command.args + path_strings
            await a_sync.run(report_part, "running {}...".format(command.command))
            result = await run(command.command, args)
            await a_sync.run(report_result, command.command, result)
            if not result.success:
                return

        await self._on_success(paths)
