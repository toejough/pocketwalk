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


# [ API ]
async def loop() -> None:
    """Loop over the pocketwalk actions."""
    await call(do_while, _loop_predicate, run_single, None)
    await call(sys.exit, 0)


async def run_single() -> None:
    """Run through the pocketwalk actions once."""
    raise NotImplementedError


# [ Internals ]
def _loop_predicate(state: typing.Any) -> None:
    assert state
    raise NotImplementedError
