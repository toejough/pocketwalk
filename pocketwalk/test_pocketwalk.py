# coding: utf-8


"""Test pocketwalk."""


# [ Imports ]
# [ -Python ]
import types
import typing
# [ -Third Party ]
# from dado import data_driven
from runaway import extras, signals, testing
import utaw
# [ -Project ]
import pocketwalk
from pocketwalk.core import checkers, commit


# [ Test Objects ]
class Loop:
    """Loop test steps."""

    def __init__(self, loop_predicate: typing.Callable[[typing.Any], bool]) -> None:
        """Init state."""
        self._loop_predicate = loop_predicate
        self._coro = testing.TestWrapper(pocketwalk.loop(self._loop_predicate))
        self._state = types.SimpleNamespace()

    def loops_single_and_gets_none(self) -> None:
        """Verify the loop call and return."""
        testing.assertEqual(
            self._coro.signal,
            signals.Call(
                extras.do_while,
                self._loop_predicate,
                pocketwalk.run_single,
                None,
            ),
        )
        self._coro.receives_value(None)

    def returns_none(self) -> None:
        """Verify the exit call and return."""
        utaw.assertIsNone(self._coro.returned)


class RunSingle:
    """Run the test steps a single time."""

    def __init__(self) -> None:
        """Init state."""
        self._coro = testing.TestWrapper(pocketwalk.run_single())
        self._state = types.SimpleNamespace()

    def runs_checkers_and_gets(self, result: checkers.Result) -> None:
        """Verify coro runs checkers and mock the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers.run))
        self._coro.receives_value(result)

    def runs_commit_and_gets(self, result: commit.Result) -> None:
        """Verify coro runs commit and mock the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(commit.run))
        self._coro.receives_value(result)

    def runs_checker_watchers_and_gets(self, result: checkers.WatchResult) -> None:
        """Verify coro runs checker watchers and mock the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers.watch))
        self._coro.receives_value(result)

    def returns(self, result: checkers.WatchResult) -> None:
        """Verify coro returns the passed in value."""
        testing.assertEqual(self._coro.returned, result)


# [ Loop Tests ]
def test_loop() -> None:
    """
    Test the main loop.

    When called, the main loop should run, and when the passed in predicate evaluates to False,
    return None.
    """
    # coverage.py flags this as a partial branch...
    the_loop = Loop(lambda state: False)  # pragma: no branch
    the_loop.loops_single_and_gets_none()
    the_loop.returns_none()


def test_run_single_happy_path() -> None:
    """Test the run_single happy path."""
    run_single = RunSingle()
    run_single.runs_checkers_and_gets(checkers.Result.PASS)
    run_single.runs_commit_and_gets(commit.Result.PASS)
    run_single.runs_checker_watchers_and_gets(checkers.WatchResult.CHANGED)
    run_single.returns(checkers.WatchResult.CHANGED)
