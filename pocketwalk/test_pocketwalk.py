# coding: utf-8


"""Test pocketwalk."""


# [ Imports ]
# [ -Python ]
import types
# [ -Third Party ]
from dado import data_driven
from runaway import extras
from runaway import signals
from runaway.testing import assertEqual, TestWrapper
# [ -Project ]
import pocketwalk
from pocketwalk.core import core


# [ Static Checking ]
# disable protected access checks - this is a test file, and we're going to
# verify use of protected attributes.
# pylint: disable=protected-access


# [ Loop ]
class Loop:
    """Loop test steps."""

    def __init__(self) -> None:
        """Init state."""
        self._coro = TestWrapper(pocketwalk.loop())
        self._state = types.SimpleNamespace()

    def loops_single_and_gets_exit_status(self, exit_status: pocketwalk.Result) -> None:
        """Verify the loop call and return."""
        assertEqual(
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
        assertEqual(self._coro.returned, self._state.status)


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
