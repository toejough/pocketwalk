# coding: utf-8


"""Core logic for pocketwalk."""


# [ Imports ]
# [ -Python ]
import typing
# [ -Third Party ]
from runaway import extras, signals
# [ -Project ]
from pocketwalk.core import checkers, source_control, types_


# [ API ]
async def loop() -> types_.Result:
    """Loop over the pocketwalk actions."""
    # mypy says this returns any...technically true?
    return await signals.call(extras.do_while, _loop_predicate, run_single, None)  # type: ignore


async def run_single() -> None:
    """Run through the pocketwalk actions once."""
    check_result = await signals.call(checkers.run)
    if check_result is checkers.Result.PASS:
        watch_future = await signals.future(checkers.watch)
        commit_future = await signals.future(source_control.commit)
        await signals.wait_for(commit_future, watch_future, minimum_done=1, cancel_remaining=True)
    else:
        await signals.call(checkers.watch)


# [ Internals ]
def _loop_predicate(state: typing.Any) -> None:
    assert state
    raise NotImplementedError
