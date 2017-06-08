# coding: utf-8


"""Check the files."""


# [ Imports ]
# [ -Python ]
import asyncio
import concurrent.futures
from pathlib import Path
from types import SimpleNamespace
from typing import Awaitable, Callable, cast, Iterable, List, Sequence
# [ -Third Party ]
import a_sync
# [ -Project ]
from ..interactors.runner import run
from ..thin_types.command import Command


# [ Helpers ]
# we are using command, but pylint doesn't think so
def report_result(command: str, result: SimpleNamespace) -> None:  # pylint: disable=unused-argument
    """Report the result."""
    # we are using outcome, but pylint doesn't think so
    outcome = 'pass' if result.success else 'fail'  # pylint: disable=unused-variable
    print('result for {command}: {outcome}'.format(**locals()))
    print("{command} output:".format(**locals()))
    print(result.output)


def _substitute(args: Sequence[str], all_path_strings: Sequence[str], changed_path_strings: Sequence[str]) -> Sequence[str]:
    """Substitute arguments."""
    args = list(args)
    all_symbol = '{all}'
    changed_symbol = '{changed}'
    substitution_occurred = False
    while all_symbol in args:
        all_index = args.index(all_symbol)
        before = args[:all_index]
        after = args[all_index + 1:]
        args = list(before) + list(all_path_strings) + list(after)
        substitution_occurred = True
    while changed_symbol in args:
        changed_index = args.index(changed_symbol)
        before = args[:changed_index]
        after = args[changed_index + 1:]
        args = list(before) + list(changed_path_strings) + list(after)
        substitution_occurred = True
    if not substitution_occurred:
        args += all_path_strings
    return args


async def _run_single(
    command: Command,
    all_path_strings: Sequence[str],
    changed_path_strings: Sequence[str],
) -> SimpleNamespace:
    """Run single command."""
    args = _substitute(command.args, all_path_strings, changed_path_strings)

    print("running {command.command}...".format(**locals()))
    try:
        result = await run(command.command, args)
    except concurrent.futures.CancelledError:
        print("result for {command.command}: cancelled".format(**locals()))
        raise
    except FileNotFoundError:
        result = SimpleNamespace(
            success=False,
            output="cannot run command ({command.command}) - no such executable found.".format(**locals()),
        )
    report_result(command.command, result)
    return result


async def _cancel_checks(pending: Iterable[asyncio.Future]) -> None:
    """Cancel the given checks."""
    if pending and not all(p.done() for p in pending):
        print("Cancelling running checks...")
        gathered = asyncio.gather(*pending)
        gathered.cancel()
        await asyncio.wait_for(gathered, timeout=None)


async def _run_parallel_checks(tasks: List[asyncio.Future]) -> bool:
    """Run the checks in parallel."""
    all_done = False
    while not all_done:
        done, pending = await asyncio.wait(tasks, return_when=concurrent.futures.FIRST_COMPLETED)
        if not all(f.result().success for f in done):
            await _cancel_checks(pending)
            return False
        all_done = not pending
    return True


# [ API ]
class Checker:
    """Checker."""

    def __init__(
        self, *,
        get_commands: Callable[[], Awaitable[Sequence[Command]]],
        get_paths: Callable[[], Awaitable[Sequence[Path]]],
        on_success: Callable[[Sequence[Path]], Awaitable[bool]]
    ) -> None:
        """Init the state."""
        self._get_commands = get_commands
        self._get_paths = get_paths
        self._unsafe_on_success = on_success
        self._changed_path_strings = []  # type: List[str]

    async def _on_success(self, paths: Sequence[Path]) -> bool:
        """Run the passed in 'on_success' function safely."""
        try:
            result = cast(bool, await a_sync.run(self._unsafe_on_success, paths))
        except concurrent.futures.CancelledError:
            raise
        # necessarily broad except here, to exit the app
        except Exception:  # pylint: disable=broad-except
            exit(1)
        return result

    async def run(self, changed_paths: Sequence[Path]) -> None:
        """Run the checks."""
        paths = await self._get_paths()
        path_strings = tuple(str(p) for p in paths)
        for the_path in changed_paths:
            the_path_string = str(the_path)
            if (
                (the_path_string not in self._changed_path_strings) and
                the_path_string in path_strings
            ):
                self._changed_path_strings.append(the_path_string)

        commands = await self._get_commands()
        tasks = []
        try:
            for command in commands:
                task = asyncio.ensure_future(_run_single(command, path_strings, self._changed_path_strings))
                tasks.append(task)
            all_passed = await _run_parallel_checks(tasks)
        except concurrent.futures.CancelledError:
            await _cancel_checks(tasks)
            raise

        success_action_succeeded = False
        if all_passed:
            success_action_succeeded = await self._on_success(paths)
        if success_action_succeeded:
            self._changed_path_strings = []
