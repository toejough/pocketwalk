# coding: utf-8


"""Core logic for pocketwalk."""


# [ Imports ]
# [ -Python ]
import sys
import typing
# [ -Third Party ]
from runaway.extras import do_while
from runaway.signals import (
    call,
)
# [ -Project ]
from pocketwalk.core import types_


# [ API ]
async def loop() -> None:
    """Loop over the pocketwalk actions."""
    status = await call(do_while, _loop_predicate, run_single, None)
    code = 0 if isinstance(status, types_.GoodExit) else 1
    await call(sys.exit, code)


async def run_single() -> None:
    """Run through the pocketwalk actions once."""
    raise NotImplementedError


# [ Internals ]
def _loop_predicate(state: typing.Any) -> None:
    assert state
    raise NotImplementedError
