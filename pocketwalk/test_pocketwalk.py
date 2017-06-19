# coding: utf-8


"""Test pocketwalk."""


# [ Imports ]
# [ -Python ]
import types
# [ -Third Party ]
from dado import data_driven
from runaway import extras, handlers, signals, testing
import utaw
# [ -Project ]
import pocketwalk
from pocketwalk.core import checkers, core, source_control


# [ Static Checking ]
# disable protected access checks - this is a test file, and we're going to
# verify use of protected attributes.
# pylint: disable=protected-access


# [ Test Objects ]
class Loop:
    """Loop test steps."""

    def __init__(self) -> None:
        """Init state."""
        self._coro = testing.TestWrapper(pocketwalk.loop())
        self._state = types.SimpleNamespace()

    def loops_single_and_gets_exit_status(self, exit_status: pocketwalk.Result) -> None:
        """Verify the loop call and return."""
        testing.assertEqual(
            self._coro.signal,
            signals.Call(
                extras.do_while,
                core._loop_predicate,
                pocketwalk.run_single,
                None,
            ),
        )
        self._coro.receives_value(exit_status)
        self._state.status = exit_status

    def returns_exit_status(self) -> None:
        """Verify the exit call and return."""
        testing.assertEqual(self._coro.returned, self._state.status)


class SinglePass:
    """Single Pass test steps."""

    def __init__(self) -> None:
        """Init state."""
        self._coro = testing.TestWrapper(pocketwalk.run_single())
        self._state = types.SimpleNamespace()

    def runs_checkers_and_gets_success(self) -> None:
        """Verify coro runs the checkers and gets success."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers.run))
        self._coro.receives_value(checkers.Result.PASS)

    def runs_checkers_and_gets_failure(self) -> None:
        """Verify coro runs the checkers and gets failure."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers.run))
        self._coro.receives_value(checkers.Result.FAIL)

    def launches_checker_watchers(self) -> None:
        """Verify coro launches the checkers' path watchers."""
        testing.assertEqual(self._coro.signal, signals.Future(checkers.watch))
        the_future = handlers.Future(checkers.watch)
        self._state.watchers_future = the_future
        self._coro.receives_value(the_future)

    def runs_checker_watchers_and_gets_success(self) -> None:
        """Verify coro runs the checker watchers and gets success."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers.watch))
        self._coro.receives_value(checkers.Result.PASS)

    def launches_commit(self) -> None:
        """Verify coro launches the commit process."""
        testing.assertEqual(self._coro.signal, signals.Future(source_control.commit))
        the_future = handlers.Future(source_control.commit)
        self._state.commit_future = the_future
        self._coro.receives_value(the_future)

    def waits_for_commit_or_watchers_and_gets_commit_success(self) -> None:
        """Verify coro waits for either the commit or watchers, and the commit returns success."""
        testing.assertEqual(self._coro.signal, signals.WaitFor(
            self._state.watchers_future, self._state.commit_future,
            minimum_done=1, cancel_remaining=False, timeout=None,
        ))
        self._state.commit_future.result = source_control.Result.PASS
        result = handlers.WaitResult([self._state.commit_future], [self._state.watchers_future], timed_out=[])
        self._coro.receives_value(result)

    def waits_for_commit_or_watchers_and_gets_watcher_success(self) -> None:
        """Verify coro waits for either the commit or watcher, and the watcher returns success."""
        testing.assertEqual(self._coro.signal, signals.WaitFor(
            self._state.watchers_future, self._state.commit_future,
            minimum_done=1, cancel_remaining=False, timeout=None,
        ))
        self._state.watchers_future.result = checkers.Result.PASS
        result = handlers.WaitResult([self._state.watchers_future], [self._state.commit_future], timed_out=[])
        self._coro.receives_value(result)

    def stops_watchers_and_gets_cancelled(self) -> None:
        """Verify coro stops watchers and gets cancelled."""
        testing.assertEqual(self._coro.signal, signals.Cancel(self._state.watchers_future))
        self._coro.receives_value(checkers.Result.CANCELLED)

    def stops_commit_and_gets_cancelled(self) -> None:
        """Verify coro stops commit and gets cancelled."""
        testing.assertEqual(self._coro.signal, signals.Cancel(self._state.commit_future))
        self._coro.receives_value(source_control.Result.CANCELLED)

    def returns_none(self) -> None:
        """Verify coro returns None."""
        utaw.assertIsNone(self._coro.returned)


# [ Loop Tests ]
@data_driven(['status'], {
    'good': [pocketwalk.Result.PASS],
    'bad': [pocketwalk.Result.FAIL],
})
def test_loop(status: pocketwalk.Result) -> None:
    """Test the main loop."""
    the_loop = Loop()
    the_loop.loops_single_and_gets_exit_status(status)
    the_loop.returns_exit_status()


# [ Single Tests ]
def test_single_happy_path() -> None:
    """Test a single pass happy path."""
    single_pass = SinglePass()
    single_pass.runs_checkers_and_gets_success()
    single_pass.launches_checker_watchers()
    single_pass.launches_commit()
    single_pass.waits_for_commit_or_watchers_and_gets_commit_success()
    single_pass.stops_watchers_and_gets_cancelled()
    single_pass.returns_none()


def test_single_failed_check() -> None:
    """Test a single pass with failed check."""
    single_pass = SinglePass()
    single_pass.runs_checkers_and_gets_failure()
    single_pass.runs_checker_watchers_and_gets_success()
    single_pass.returns_none()


def test_single_change_during_commit() -> None:
    """Test a single pass with failed check."""
    single_pass = SinglePass()
    single_pass.runs_checkers_and_gets_success()
    single_pass.launches_checker_watchers()
    single_pass.launches_commit()
    single_pass.waits_for_commit_or_watchers_and_gets_watcher_success()
    single_pass.stops_commit_and_gets_cancelled()
    single_pass.returns_none()
