# coding: utf-8


"""Test pocketwalk."""


# [ Imports ]
# [ -Python ]
import sys
# [ -Third Party ]
from runaway.extras import do_while
from runaway.signals import (
    Call,
)
from runaway.testing import assertEqual, TestWrapper
# [ -Project ]
from . import loop, run_single
from .core import _loop_predicate, types_


# [ Loop ]
class Loop:
    """Loop test steps."""

    def __init__(self) -> None:
        """Init state."""
        self._coro = TestWrapper(loop())

    def loops_single_and_gets_exit_status(self, exit_status: types_.GoodExit) -> None:
        """Verify the loop call and return."""
        assertEqual(
            self._coro.signal,
            Call(
                do_while,
                _loop_predicate,
                run_single,
                None,
            ),
        )
        self._coro.receives_value(exit_status)

    def exits_and_gets_system_exit(self, exit_code: int) -> None:
        """Verify the exit call and return."""
        assertEqual(self._coro.signal, Call(sys.exit, exit_code))
        self._coro.receives_error(SystemExit, SystemExit(exit_code), None)


# [ Loop Tests ]
def test_loop() -> None:
    """Test the main loop."""
    the_loop = Loop()
    exit_status = types_.GoodExit()
    system_exit_code = 0
    the_loop.loops_single_and_gets_exit_status(exit_status)
    the_loop.exits_and_gets_system_exit(system_exit_code)
