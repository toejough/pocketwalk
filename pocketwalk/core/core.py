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
async def loop(predicate: typing.Callable[[typing.Any], bool]) -> checkers.Result:
    """
    Loop over the pocketwalk core actions.

    ---
    Return when the passed in predicate indicates.
    ---

    args:
        - predicate: a predicate function taking one arbitrary state object (the output of `run_single`),
          and returning `True` if the loop should continue running and `False` if it should stop.

    returns: the final arbitrary state.
    """
    return typing.cast(checkers.Result, await signals.call(extras.do_while, predicate, run_single, None))


async def run_single() -> checkers.WatchResult:
    """Run through the pocketwalk actions once."""
    typing.cast(checkers.Result, await signals.call(checkers.run_until_all_pass))
    typing.cast(commit.Result, await signals.call(commit.run))
    return typing.cast(checkers.WatchResult, await signals.call(checkers.watch_until_change))
