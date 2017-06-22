# coding: utf-8


"""Test pocketwalk."""


# [ Imports ]
# [ -Python ]
import types
import typing
# [ -Third Party ]
from dado import data_driven
from runaway import extras, signals, testing
import utaw
# [ -Project ]
import pocketwalk
from pocketwalk.core import checkers, core, source_control


# [ Static Checking ]
# disable protected access checks - this is a test file, and we're going to
# verify use of protected attributes.
# pylint: disable=protected-access
# pylint doesn't know this is a typedef
AnyResult = typing.Union[checkers.Result, checkers.WatchResult]  # pylint: disable=invalid-name


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

    def runs_checkers_and_gets(self, result: checkers.Result) -> None:
        """Verify coro runs the checkers and gets the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers.run))
        self._coro.receives_value(result)

    def runs_watched_commit_and_gets(self, result: AnyResult) -> None:
        """Verify coro runs a watched commit and gets the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(core._do_watched_commit))
        self._coro.receives_value(result)

    def runs_watchers_and_gets(self, result: checkers.WatchResult) -> None:
        """Verify coro runs watchers and gets the given result."""
        testing.assertEqual(self._coro.signal, signals.Call(checkers.watch))
        self._coro.receives_value(result)

    def returns(self, result: core.types_.Result) -> None:
        """Verify coro returns the result."""
        utaw.assertIs(self._coro.returned, result)


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
    single_pass.runs_checkers_and_gets(checkers.Result.PASS)
    single_pass.runs_watched_commit_and_gets(source_control.Result.PASS)
    single_pass.returns(core.types_.Result.PASS)


def test_single_failed_check() -> None:
    """Test a single pass with failed check."""
    single_pass = SinglePass()
    single_pass.runs_checkers_and_gets(checkers.Result.FAIL)
    single_pass.runs_watchers_and_gets(checkers.WatchResult.CHANGED)
    single_pass.returns(core.types_.Result.PASS)


def test_single_exit_during_check() -> None:
    """Test a single pass with exit signal during check."""
    single_pass = SinglePass()
    single_pass.runs_checkers_and_gets(checkers.Result.EXIT)
    single_pass.returns(core.types_.Result.EXIT)


def test_single_change_during_commit() -> None:
    """Test a single pass with change during commit."""
    single_pass = SinglePass()
    single_pass.runs_checkers_and_gets(checkers.Result.PASS)
    single_pass.runs_watched_commit_and_gets(checkers.WatchResult.CHANGED)
    single_pass.returns(core.types_.Result.PASS)


def test_single_exit_during_commit() -> None:
    """Test a single pass with exit signal during commit."""
    single_pass = SinglePass()
    single_pass.runs_checkers_and_gets(checkers.Result.PASS)
    single_pass.runs_watched_commit_and_gets(checkers.Result.EXIT)
    single_pass.returns(core.types_.Result.EXIT)


def test_single_failed_commit() -> None:
    """Test a single pass with a failed commit."""
    single_pass = SinglePass()
    single_pass.runs_checkers_and_gets(checkers.Result.PASS)
    single_pass.runs_watched_commit_and_gets(source_control.Result.FAIL)
    single_pass.returns(core.types_.Result.FAIL)
