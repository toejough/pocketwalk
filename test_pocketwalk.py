# coding: utf-8


"""
Test pocketwalk.

What gets tested:
* functions of the form 'if this, then that' need specific examples of data in, data out.a

What does not get tested:
* functions of the form 'do these things'

Features:
    * run a tool and report its result (test_run_multiple_tools)
    * run multiple tools simultaneously (test_run_multiple_tools)
    * skip running a tool if conditions haven't changed since last completed run (test_running_tools)
    * repeat a tool until the outcome is success, waiting for conditions to change in between runs (test_running_tools)
    * restart a running tool if conditions change during a run
    * wait to run a tool until other tools pass
    * stop running a tool if tool removed while running
    * start running a tool if tool added
    * if not single run, repeat tools forever, waiting for conditions to change between runs
    * cancel running tools and report cancelled and last aggregate result (max RC)
    * VCS commit
"""


# [ Imports ]
# [ -Python ]
import enum
import typing
import sys
from unittest.mock import sentinel, MagicMock
# [ -Third Party ]
import dado
from runaway import signals, testing, handlers
import utaw
# [ -Project ]
from pocketwalk.core import Core


# pylint: disable=protected-access
# this is a test module.  we're testing protected-access members


# [ Tests ]
# XXX refactor test?  loop args?
@dado.data_driven([
    'cancelled',
    'loop_forever',
    'vcs_running',
    'loop_till_pass',
    'all_tools_passed',
    'any_tools_not_done',
    'result',
], {
    'cancelled': [True, None, None, None, None, None, False],
    'loop_forever': [False, True, None, None, None, None, True],
    'vcs_running': [False, False, True, None, None, None, True],
    'till_pass_not_passing': [False, False, False, True, False, None, True],
    'till_pass_passing': [False, False, False, True, True, False, False],
    'any_tools_not_done': [False, False, False, False, None, True, True],
    'all_tools_done': [False, False, False, False, None, False, False],
})  # pylint: disable=too-many-arguments
def test_should_loop(cancelled, loop_forever, vcs_running, loop_till_pass, all_tools_passed, any_tools_not_done, result):
    """Test the should loop behavior."""
    tool_runner = MagicMock()
    config = MagicMock()
    vcs = MagicMock()
    cancellation = MagicMock()
    core = Core(context_manager=None, tool_runner=tool_runner, config=config, vcs=vcs, cancellation=cancellation)
    tester = Tester(core._should_loop).called_with_args(sentinel.tools)
    tester.calls(cancellation.cancelled).with_args()
    tester.receives(cancelled)
    if cancelled:
        return tester.returns(result)
    tester.calls(config.loop_forever).with_args()
    tester.receives(loop_forever)
    if loop_forever:
        return tester.returns(result)
    tester.calls(vcs.vcs_running).with_args()
    tester.receives(vcs_running)
    if vcs_running:
        return tester.returns(result)
    tester.calls(config.loop_till_pass).with_args()
    tester.receives(loop_till_pass)
    if loop_till_pass:
        tester.calls(tool_runner.all_tools_passed).with_args(sentinel.tools)
        tester.receives(all_tools_passed)
        if not all_tools_passed:
            return tester.returns(result)
    tester.calls(tool_runner.any_tools_not_done).with_args()
    tester.receives(any_tools_not_done)
    return tester.returns(result)


def is_coro(maybe_coro: typing.Any) -> bool:
    """Return whether or not the thing is a coro."""
    try:
        return bool(
            maybe_coro.send and
            maybe_coro.throw and
            maybe_coro.close  # noqa: C812 - single statement for a single arg func, trailing comma makes no sense.
        )
    except AttributeError:
        return False


class Sentinels(enum.Enum):
    """Sentinel states."""

    NOT_SET = enum.auto()


class DoNotUse:
    """An object not to be used."""

    def __getattr__(self, name: str) -> None:
        """Raise an exception if any part of this is accessed."""
        raise RuntimeError("This object is not supposed to be used, but it was.  Test or FUT needs updating!")


class Tester:
    """A tester wrapper."""

    # XXX make a copy replay io, rather than taking the current coro

    def __init__(self, function: typing.Callable) -> None:
        """Init the state."""
        self._function = function
        self._coro = None
        self._return_value = Sentinels.NOT_SET
        self._exc_info = Sentinels.NOT_SET
        self._last_output = Sentinels.NOT_SET

    def called_with_args(self, *args: typing.Any, **kwargs: typing.Any) -> "Tester":
        """Call the function with those args."""
        result = self._function(*args, **kwargs)
        if is_coro(result):
            self._coro = result
            try:
                self._last_output = self._coro.send(None)
            except StopIteration as error:
                self._last_output = error.value
                self._return_value = error.value
            # necessarily broad exception - we're recording any exception
            except Exception:  # pylint: disable=broad-except
                self._last_output = sys.exc_info()
                self._exc_info = self._last_output
        else:
            self._last_output = result
            self._return_value = result
        return self

    def waits_for(
        self, *futures: handlers.Future,
        minimum_done: typing.Optional[int]=None,
        cancel_remaining: bool=True,
        timeout: typing.Optional[float]=None,
    ) -> "Tester":
        """Assert that the coro waits for the given futures."""
        if self._return_value is not Sentinels.NOT_SET:
            raise RuntimeError(f"The function ({self._function}) already returned ({self._return_value})")
        if self._exc_info is not Sentinels.NOT_SET:
            raise self._exc_info[1].with_traceback(self._exc_info[2])
        testing.assertEqual(self._last_output, signals.WaitFor(
            *futures, minimum_done=minimum_done, cancel_remaining=cancel_remaining, timeout=timeout,
        ))
        return self

    def mutation_occurs(self, mutation: typing.Callable) -> "Tester":
        """Mutate some state."""
        mutation()
        return self

    def receives_any(self) -> "Tester":
        """Send a sentinel value that errors if called or accessed."""
        if self._coro is None:
            raise RuntimeError("Coroutine has not been set!")
        try:
            args = (DoNotUse(),)
            kwargs = {}  # type: dict
            self._last_output = self._coro.send(*args, **kwargs)
        except StopIteration as error:
            self._last_output = error.value
            self._return_value = error.value
        # necessarily broad exception - we're recording any exception
        except Exception:  # pylint: disable=broad-except
            self._last_output = sys.exc_info()
            self._exc_info = self._last_output

        return self

    def creates_future_for(self, function: typing.Callable) -> "Tester":
        """Assert that the coro creates a future for the given function."""
        if self._return_value is not Sentinels.NOT_SET:
            raise RuntimeError(f"The function ({self._function}) already returned ({self._return_value})")
        if self._exc_info is not Sentinels.NOT_SET:
            raise self._exc_info[1].with_traceback(self._exc_info[2])
        utaw.assertIsInstance(self._last_output, signals.Future)
        utaw.assertEqual(self._last_output.func, function)
        return self

    def calls(self, function: typing.Callable) -> "Tester":
        """Assert that the coro calls the given function."""
        if self._return_value is not Sentinels.NOT_SET:
            raise RuntimeError(f"The function ({self._function}) already returned ({self._return_value})")
        if self._exc_info is not Sentinels.NOT_SET:
            raise self._exc_info[1].with_traceback(self._exc_info[2])
        utaw.assertIsInstance(self._last_output, signals.Call)
        utaw.assertEqual(self._last_output.func, function)
        return self

    def sleeps(self, seconds) -> "Tester":
        """Assert that the coro sleeps for the given time."""
        if self._return_value is not Sentinels.NOT_SET:
            raise RuntimeError(f"The function ({self._function}) already returned ({self._return_value})")
        if self._exc_info is not Sentinels.NOT_SET:
            raise self._exc_info[1].with_traceback(self._exc_info[2])
        utaw.assertIsInstance(self._last_output, signals.Sleep)
        utaw.assertEqual(self._last_output.seconds, seconds)
        return self

    def with_args(self, *args: typing.Any, **kwargs: typing.Any) -> "Tester":
        """Assert that the coro called the last thing with the given args."""
        if self._return_value is not Sentinels.NOT_SET:
            raise RuntimeError(f"The function ({self._function}) already returned ({self._return_value})")
        if self._exc_info is not Sentinels.NOT_SET:
            raise self._exc_info[1].with_traceback(self._exc_info[2])
        func = self._last_output.func
        testing.assertEqual(self._last_output, type(self._last_output)(func, *args, **kwargs))
        return self

    def receives(self, args: typing.Any) -> "Tester":
        """Send the given value."""
        if self._coro is None:
            raise RuntimeError("Coroutine has not been set!")
        try:
            self._last_output = self._coro.send(args)
        except StopIteration as error:
            self._last_output = error.value
            self._return_value = error.value
        # necessarily broad exception - we're recording any exception
        except Exception:  # pylint: disable=broad-except
            self._last_output = sys.exc_info()
            self._exc_info = self._last_output

        return self

    def receives_exception(self, exception: Exception) -> "Tester":
        """Raise an exception."""
        if self._coro is None:
            raise RuntimeError("Coroutine has not been set!")
        try:
            self._last_output = self._coro.throw(exception)
        except StopIteration as error:
            self._last_output = error.value
            self._return_value = error.value
        # necessarily broad exception - we're recording any exception
        except Exception:  # pylint: disable=broad-except
            self._last_output = sys.exc_info()
            self._exc_info = self._last_output

        return self

    def returns(self, value: typing.Any) -> "Tester":
        """Verify the coro returned the given value."""
        if self._exc_info is not Sentinels.NOT_SET:
            raise self._exc_info[1].with_traceback(self._exc_info[2])
        if self._return_value is Sentinels.NOT_SET:
            raise RuntimeError(f"The function ({self._function}) has not yet returned")
        testing.assertEqual(self._return_value, value)
        return self


# [ Vulture ]
# these are whitelistings for vulture
# pylint: disable=pointless-statement
Tester.waits_for
Tester.mutation_occurs
Tester.receives_any
Tester.creates_future_for
Tester.sleeps
Tester.receives_exception
# pylint: enable=pointless-statement
