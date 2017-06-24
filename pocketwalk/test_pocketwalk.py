# coding: utf-8


"""Test pocketwalk."""


# [ Imports ]
# [ -Third Party ]
from runaway import extras, signals, testing
import utaw
# [ -Project ]
import pocketwalk
from pocketwalk.core import checkers, commit


# [ Static Checking ]
# this is a test module - we're doing protected accesses.
# pylint: disable=protected-access


# [ Test Objects ]
class Loop:
    """Loop test steps."""

    def __init__(self) -> None:
        """Init state."""
        self._coro = testing.TestWrapper(pocketwalk.loop())

    def loops_single(self) -> None:
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

    def returns(self) -> None:
        """Verify the exit call and return."""
        utaw.assertIsNone(self._coro.returned)


class RunSingle:
    """Run the test steps a single time."""

    def __init__(self) -> None:
        """Init state."""
        self._coro = testing.TestWrapper(pocketwalk.run_single())

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


class CheckerLoop:
    """Checker loop test steps."""

    def __init__(self) -> None:
        """Init state."""
        self._coro = testing.TestWrapper(checkers.run_until_all_pass())

    def loops_single(self) -> None:
        """Verify the loop call and return."""
        testing.assertEqual(
            self._coro.signal,
            signals.Call(
                extras.do_while,
                checkers._not_all_passing,
                checkers._run_single,
                None,
            ),
        )
        self._coro.receives_value(None)

    def returns(self) -> None:
        """Verify the exit call and return."""
        utaw.assertIsNone(self._coro.returned)


class CheckerRunSingle:
    """Run the checker steps a single time."""

    def __init__(self) -> None:
        """Init state."""
        self._coro = testing.TestWrapper(checkers._run_single(None))

    def gets_checker_list_and_receives_list(self) -> None:
        """Verify coro runs checkers and mock the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers._get_checker_list))
        self._coro.receives_value(None)

    def cancels_removed_checkers(self) -> None:
        """Verify coro cancels removed checkers and mock the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers._cancel_removed_checkers))
        self._coro.receives_value(None)

    def launches_new_checkers(self) -> None:
        """Verify coro launches new checkers and mock the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers._launch_new_checkers))
        self._coro.receives_value(None)

    def relaunches_changed_checkers(self) -> None:
        """Verify coro relaunches changed checkers and mock the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers._relaunch_changed_checkers))
        self._coro.receives_value(None)

    def launches_watchers_for_completed_checkers(self) -> None:
        """Verify coro launches watchers for completed checkers and mock the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers._launch_watchers_for_completed_checkers))
        self._coro.receives_value(None)

    def launches_watcher_for_checker_list(self) -> None:
        """Verify coro launches watcher for checker list and mock the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers._launch_watcher_for_checker_list))
        self._coro.receives_value(None)

    def waits_for_any_future(self) -> None:
        """Verify coro waits for any future and mock the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers._wait_for_any_future))
        self._coro.receives_value(None)

    def analyzes_checker_state_and_gets(self, status: checkers.Result) -> None:
        """Verify coro waits for any future and mock the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers._analyze_checker_state))
        self._coro.receives_value(status)

    def cancels_all_futures(self) -> None:
        """Verify coro cancels all futures and mock the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers._cancel_all_futures))
        self._coro.receives_value(None)

    def returns(self, status: checkers.Result) -> None:
        """Verify coro returns given status."""
        testing.assertEqual(self._coro.returned, status)


# [ Loop Tests ]
def test_loop() -> None:
    """
    Test the main loop.

    When called, the main loop should run, and when the passed in predicate evaluates to False,
    return None.
    """
    the_loop = Loop()
    the_loop.loops_single()
    the_loop.returns()


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


# [ Checkers ]
def test_checker_loop() -> None:
    """Test the run_checkers happy path."""
    checker_loop = CheckerLoop()
    checker_loop.loops_single()
    checker_loop.returns()


def test_checker_run_single_running() -> None:
    """Test the single run for the checkers while checkers are running."""
    run_single = CheckerRunSingle()
    run_single.gets_checker_list_and_receives_list()
    run_single.cancels_removed_checkers()
    run_single.launches_new_checkers()
    run_single.relaunches_changed_checkers()
    run_single.launches_watchers_for_completed_checkers()
    run_single.launches_watcher_for_checker_list()
    run_single.waits_for_any_future()
    run_single.analyzes_checker_state_and_gets(checkers.Result.RUNNING)
    run_single.returns(checkers.Result.RUNNING)


def test_checker_run_single_all_passing() -> None:
    """Test the single run for the checkers while checkers are running."""
    run_single = CheckerRunSingle()
    run_single.gets_checker_list_and_receives_list()
    run_single.cancels_removed_checkers()
    run_single.launches_new_checkers()
    run_single.relaunches_changed_checkers()
    run_single.launches_watchers_for_completed_checkers()
    run_single.launches_watcher_for_checker_list()
    run_single.waits_for_any_future()
    run_single.analyzes_checker_state_and_gets(checkers.Result.ALL_PASSING)
    run_single.cancels_all_futures()
    run_single.returns(checkers.Result.ALL_PASSING)
