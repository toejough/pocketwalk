# coding: utf-8


"""Test pocketwalk."""


# [ Imports ]
# [ -Python ]
import types
# [ -Third Party ]
from runaway import extras, signals, testing
import utaw
# [ -Project ]
import pocketwalk
from pocketwalk.core import checkers, commit


# [ Test Objects ]
class Loop:
    """Loop test steps."""

    def __init__(self) -> None:
        """Init state."""
        self._coro = testing.TestWrapper(pocketwalk.loop())
        self._state = types.SimpleNamespace()

    def loops_single_and_gets_none(self) -> None:
        """Verify the loop call and return."""
        testing.assertEqual(
            self._coro.signal,
            signals.Call(
                extras.run_forever,
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

    def runs_checkers_until_all_pass(self) -> None:
        """Verify coro runs checkers and mock the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers.run_until_all_pass))
        self._coro.receives_value(None)

    def runs_commit_and_gets(self, result: commit.Result) -> None:
        """Verify coro runs commit and mock the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(commit.run))
        self._coro.receives_value(result)

    def runs_checker_watchers_until_change(self) -> None:
        """Verify coro runs checker watchers and mock the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers.watch_until_change))
        self._coro.receives_value(None)

    def returns_none(self) -> None:
        """Verify coro returns None."""
        utaw.assertIsNone(self._coro.returned)


# [ Loop Tests ]
def test_loop() -> None:
    """
    Test the main loop.

    When called, the main loop should run, and when the passed in predicate evaluates to False,
    return None.
    """
    the_loop = Loop()
    the_loop.loops_single_and_gets_none()
    the_loop.returns_none()


def test_run_single_happy_path() -> None:
    """Test the run_single happy path."""
    run_single = RunSingle()
    run_single.runs_checkers_until_all_pass()
    run_single.runs_commit_and_gets(commit.Result.COMMITTED)
    run_single.runs_checker_watchers_until_change()
    run_single.returns_none()


def test_run_single_change_during_commit() -> None:
    """Test the run_single path when there is a change during a commit."""
    run_single = RunSingle()
    run_single.runs_checkers_until_all_pass()
    run_single.runs_commit_and_gets(commit.Result.CHANGES_DETECTED)
    run_single.returns_none()
