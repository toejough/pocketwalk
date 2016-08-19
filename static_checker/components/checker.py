"""Check the files."""


# [ Imports ]
# [ -Python ]
import logging
from typing import Sequence, Callable, Awaitable, Set
from pathlib import Path
from types import SimpleNamespace
import asyncio
import concurrent.futures
# [ -Third Party ]
import a_sync
# [ -Project ]
from ..interactors.runner import run
from ..thin_types.command import Command


# [ Logging ]
logger = logging.getLogger(__name__)


# [ Helpers ]
def report_result(command: str, result: SimpleNamespace) -> None:
    """Report the result."""
    outcome = 'pass' if result.success else 'fail'
    print('result for {}: {}'.format(command, outcome))
    if not result.success:
        print("{} output:".format(command))
        print(result.output)


async def _run_single(command: Command, path_strings: Sequence[str]) -> SimpleNamespace:
    """Run single command."""
    args = command.args + path_strings
    await a_sync.run(print, "running {}...".format(command.command))
    try:
        result = await run(command.command, args)
    except concurrent.futures.CancelledError:
        await a_sync.run(print, "result for {}: cancelled".format(command.command))
        raise
    await a_sync.run(report_result, command.command, result)
    return result


async def _cancel_checks(pending: Set[asyncio.Future]) -> None:
    """Cancel the given checks."""
    print("Cancelling pending checks due to check failure.")
    # XXX mypy says there is no gather
    gathered = asyncio.gather(*pending)  # type: ignore
    gathered.cancel()
    await asyncio.wait_for(gathered, timeout=None)


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

        commands = await self._get_commands()
        tasks = []
        stop = False
        try:
            for command in commands:
                # XXX colored check/x
                # XXX bold current command
                # XXX normal old command
                # XXX mypy says asyncio doesn't have ensure_future
                task = asyncio.ensure_future(_run_single(command, path_strings))  # type: ignore
                tasks.append(task)
            while not stop:
                done, pending = await asyncio.wait(tasks, return_when=concurrent.futures.FIRST_COMPLETED)
                if not all(f.result().success for f in done):
                    await _cancel_checks(pending)
                    return
                stop = not pending
        except concurrent.futures.CancelledError:
            logger.info("checking cancelled - cancelling running checks")
            for task in tasks:
                task.cancel()
            raise

        await self._on_success(paths)
