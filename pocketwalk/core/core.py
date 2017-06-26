# coding: utf-8


"""Core logic for pocketwalk."""


# [ Imports ]
# [ -Python ]
import typing
# [ -Third Party ]
from runaway import extras, signals
# [ -Project ]
from pocketwalk.core import checkers, commit


# [ API ]
async def loop() -> None:
    """Loop over the pocketwalk core actions."""
    await signals.call(extras.run_forever, run_single, None)


async def run_single(_state: None=None) -> commit.Result:
    """Run through the pocketwalk actions once."""
    await signals.call(checkers.run_until_all_pass)
    return typing.cast(commit.Result, await signals.call(commit.run))
