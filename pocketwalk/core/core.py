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


async def run_single() -> types_.Result:
    """Run through the pocketwalk actions once."""
    check_result = await signals.call(checkers.run)
    if check_result is checkers.Result.PASS:
        commit_result = await signals.call(_do_watched_commit)
        if commit_result is source_control.Result.FAIL:
            return types_.Result.FAIL
        elif commit_result is source_control.Result.EXIT:
            return types_.Result.EXIT
    elif check_result is checkers.Result.FAIL:
        await signals.call(checkers.watch)
    else:
        return types_.Result.EXIT
    return types_.Result.PASS


# [ Internals ]
def _loop_predicate(state: typing.Any) -> None:
    assert state
    raise NotImplementedError


async def _do_watched_commit() -> None:
    """Perform a watched commit."""
    watch_future = await signals.future(checkers.watch)
    commit_future = await signals.future(source_control.commit)
    await signals.wait_for(commit_future, watch_future, minimum_done=1, cancel_remaining=True)
