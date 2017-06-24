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


# [ Static Checking ]
# disable protected access checks - this is a test file, and we're going to
# verify use of protected attributes.
# pylint: disable=protected-access
# pylint doesn't know this is a typedef
# AnyResult = typing.Union[checkers.Result, checkers.WatchResult]  # pylint: disable=invalid-name
# ResultOrCommand = typing.Union[checkers.Result, pocketwalk.Command]  # pylint: disable=invalid-name
# AnyResultOrCommand = typing.Union[AnyResult, pocketwalk.Command]  # pylint: disable=invalid-name
# WatchResultOrCommand = typing.Union[checkers.WatchResult, pocketwalk.Command]  # pylint: disable=invalid-name


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


# class LoopReturn:
#     """Loop return test steps."""

#     def __init__(self, status: ResultOrCommand) -> None:
#         """Init state."""
#         self._status = status

#         async def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
#             """Coro wrapper."""
#             return core._loop_predicate(*args, **kwargs)

#         self._coro = testing.TestWrapper(wrapper(status))

#     def returns(self, should_return: bool) -> None:
#         """Verify coro returns the result."""
#         utaw.assertIs(self._coro.returned, should_return)


# class CheckerRun:
#     """Run the Checker."""

#     def __init__(self) -> None:
#         """Init state."""
#         self._coro = testing.TestWrapper(core.run_checks())
#         self._state = types.SimpleNamespace()

#     def launches_checker_loop_and_gets(self, checker_loop_future: handlers.Future) -> None:
#         """Launches checker loop and gets future."""
#         testing.assertEqual(
#             self._coro.signal,
#             signals.Future(checkers.loop),
#         )
#         self._coro.receives_value(checker_loop_future)

#     def launches_command_watcher_loop_and_gets(self, command_watcher_loop_future: handlers.Future) -> None:
#         """Launches command watcher loop and gets future."""
#         testing.assertEqual(
#             self._coro.signal,
#             signals.Future(core._watch_for_command),
#         )
#         self._coro.receives_value(command_watcher_loop_future)


# class CheckerLoop:
#     """Checker loop test steps."""

#     def __init__(self) -> None:
#         """Init state."""
#         self._coro = testing.TestWrapper(checkers.loop())
#         self._state = types.SimpleNamespace()

#     def loops_single_and_gets_exit_status(self, exit_status: ResultOrCommand) -> None:
#         """Verify the loop call and return."""
#         testing.assertEqual(
#             self._coro.signal,
#             signals.Call(
#                 extras.do_while,
#                 checkers._loop_predicate,
#                 checkers._run_single,
#                 None,
#             ),
#         )
#         self._coro.receives_value(exit_status)
#         self._state.status = exit_status

#     def returns_exit_status(self) -> None:
#         """Verify the exit call and return."""
#         testing.assertEqual(self._coro.returned, self._state.status)


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
    # run_single.runs_checker_watchers_and_gets(checkers.WatchResult.CHANGED)
    # run_single.returns(checkers.WatchResult.CHANGED)


# # [ Single Tests ]
# # First branch
# def test_single_happy_path() -> None:
#     """Test a single pass happy path."""
#     single_pass = SinglePass()
#     single_pass.runs_checkers_and_gets(checkers.Result.PASS)
#     single_pass.runs_watched_commit_and_gets(source_control.Result.PASS)
#     single_pass.returns(core.types_.Result.PASS)


# def test_single_failed_check() -> None:
#     """Test a single pass with failed check."""
#     single_pass = SinglePass()
#     single_pass.runs_checkers_and_gets(checkers.Result.FAIL)
#     single_pass.runs_watchers_and_gets(checkers.WatchResult.CHANGED)
#     single_pass.returns(core.types_.Result.PASS)


# def test_single_exit_during_check() -> None:
#     """Test a single pass with exit signal during check."""
#     single_pass = SinglePass()
#     single_pass.runs_checkers_and_gets(pocketwalk.Command.EXIT)
#     single_pass.returns(pocketwalk.Command.EXIT)


# # Second Branch - after pass
# def test_single_change_during_commit() -> None:
#     """Test a single pass with change during commit."""
#     single_pass = SinglePass()
#     single_pass.runs_checkers_and_gets(checkers.Result.PASS)
#     single_pass.runs_watched_commit_and_gets(checkers.WatchResult.CHANGED)
#     single_pass.returns(core.types_.Result.PASS)


# def test_single_failed_commit() -> None:
#     """Test a single pass with a failed commit."""
#     single_pass = SinglePass()
#     single_pass.runs_checkers_and_gets(checkers.Result.PASS)
#     single_pass.runs_watched_commit_and_gets(source_control.Result.FAIL)
#     single_pass.returns(core.types_.Result.FAIL)


# def test_single_exit_during_commit() -> None:
#     """Test a single pass with exit signal during commit."""
#     single_pass = SinglePass()
#     single_pass.runs_checkers_and_gets(checkers.Result.PASS)
#     single_pass.runs_watched_commit_and_gets(pocketwalk.Command.EXIT)
#     single_pass.returns(pocketwalk.Command.EXIT)


# # Second Branch - after fail
# def test_single_failed_check_and_exit_during_watch() -> None:
#     """Test a single pass with failed check, and exiting during watch."""
#     single_pass = SinglePass()
#     single_pass.runs_checkers_and_gets(checkers.Result.FAIL)
#     single_pass.runs_watchers_and_gets(pocketwalk.Command.EXIT)
#     single_pass.returns(pocketwalk.Command.EXIT)


# # [ Loop Predicate Tests ]
# @data_driven(['status', 'should_return'], {
#     'good': [checkers.Result.PASS, True],
#     'bad': [checkers.Result.FAIL, True],
#     'exit': [pocketwalk.Command.EXIT, False],
# })
# def test_loop_return_on(status: ResultOrCommand, should_return: bool) -> None:
#     """Test the loop return conditions."""
#     loop_return = LoopReturn(status)
#     loop_return.returns(should_return)


# # [ Checker Run Tests ]
# def test_checker_run() -> None:
#     """Test running checkers."""
#     checker_run = CheckerRun()
#     checker_future = handlers.Future(checkers.loop)
#     checker_run.launches_checker_loop_and_gets(checker_future)
#     command_watcher_future = handlers.Future(core._watch_for_command)
#     checker_run.launches_command_watcher_loop_and_gets(command_watcher_future)
#     # checker_run.waits_for_checker_or_command_and_gets(handlers.WaitResult([checker_future], [command_watcher_future], []))
#     # checker_run.returns(pocketwalk.Command.EXIT)


# # [ Checker Loop Tests ]
# @data_driven(['status'], {
#     'good': [checkers.Result.PASS],
#     'bad': [checkers.Result.FAIL],
#     'exit': [pocketwalk.Command.EXIT],
# })
# def test_checker_loop(status: ResultOrCommand) -> None:
#     """Test the main loop."""
#     the_loop = CheckerLoop()
#     the_loop.loops_single_and_gets_exit_status(status)
#     the_loop.returns_exit_status()


# # [ Checker Single Run ]
# # def test_checker_single_happy_path() -> None:
# #     """Test Checker single run."""
# #     checker_single = CheckerSingle()


# # if not running, launch checker_list watcher
# # launch queued checkers
# # cancel removed checkers
# # cancel removed watchers
# # launch watchers for finished checkers
# # wait for running checkers, running_watchers, or checker list update
# # update state
# # return state

# # keep looping if any checkers still running
