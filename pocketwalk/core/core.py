# coding: utf-8


"""Core logic for pocketwalk."""


# [ Imports ]
# [ -Python ]
import typing
# [ -Third Party ]
from runaway import extras, signals
# [ -Project ]
from pocketwalk.core import types_


# [ Static Checking ]
# pylint doesn't know this is a typedef
# ResultOrCommand = typing.Union[checkers.Result, types_.Command]  # pylint: disable=invalid-name


# [ API ]
async def loop(predicate: typing.Callable[[typing.Any], bool]) -> types_.Result:
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
    # mypy says this returns any...technically true?
    return await signals.call(extras.do_while, predicate, run_single, None)  # type: ignore


async def run_single() -> typing.Any:
    """Run through the pocketwalk actions once."""
    raise NotImplementedError
    # check_result = await signals.call(run_checks)
    # if check_result is checkers.Result.PASS:
    #     commit_result = await signals.call(_do_watched_commit)
    #     if commit_result is source_control.Result.FAIL:
    #         return types_.Result.FAIL
    #     elif commit_result is types_.Command.EXIT:
    #         return types_.Command.EXIT
    # elif check_result is checkers.Result.FAIL:
    #     checker_result = await signals.call(checkers.watch)
    #     if checker_result is checkers.WatchResult.CHANGED:
    #         return types_.Result.PASS
    #     elif checker_result is types_.Command.EXIT:
    #         return types_.Command.EXIT
    # else:
    #     return types_.Command.EXIT
    # return types_.Result.PASS


# async def run_checks() -> ResultOrCommand:
#     """Run the checkers and the command watcher."""
#     checker_future = await signals.future(checkers.loop)
#     command_future = await signals.future(_watch_for_command)
#     results = await signals.wait_for(checker_future, command_future, minimum_done=1)
#     # mypy thinks this is type any
#     return results[0].result  # type: ignore


# # [ Internals ]
# def _loop_predicate(state: ResultOrCommand) -> bool:
#     return state is not types_.Command.EXIT


# async def _do_watched_commit() -> None:
#     """Perform a watched commit."""
#     watch_future = await signals.future(checkers.watch)
#     commit_future = await signals.future(source_control.commit)
#     await signals.wait_for(commit_future, watch_future, minimum_done=1, cancel_remaining=True)


# async def _watch_for_command() -> None:
#     """Watch for a command."""
#     raise NotImplementedError
