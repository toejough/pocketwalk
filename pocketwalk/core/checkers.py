# coding: utf-8


"""Checker logic for pocketwalk."""


# [ Import ]
# [ -Python ]
import enum
import typing
# [ -Third Party ]
from runaway import extras, signals
# [ -Project ]
# from pocketwalk.core.types_ import Result


# [ API ]
class Result(enum.Enum):
    """Result enums."""

    PASS = enum.auto()
    FAIL = enum.auto()


class WatchResult(enum.Enum):
    """WatchResult enums."""

    CHANGED = enum.auto()


async def run_until_all_pass() -> None:
    """Run the checkers until they all pass."""
    await signals.call(extras.do_while, _not_all_passing, _run_single, None)


def watch_until_change() -> WatchResult:
    """Run the watchers until a change."""
    raise NotImplementedError  # pragma: no cover


# def watch() -> WatchResult:
#     """Watch the static checker files concurrently."""
#     return WatchResult.CHANGED


# [ Internals ]
async def _run_single(state: typing.Any) -> typing.Any:
    """Run a single iteration of checker actions."""
    await signals.call(_get_checker_list)
    await signals.call(_cancel_removed_checkers)
    await signals.call(_launches_new_checkers)
    return state


def _not_all_passing(state: typing.Any) -> bool:
    """Test whether or not to continue the loop."""
    raise NotImplementedError(state)  # pragma: no cover


def _get_checker_list() -> list:
    """Return the checker list."""
    raise NotImplementedError()  # pragma: no cover


def _cancel_removed_checkers() -> None:
    """Cancel the removed checkers."""
    raise NotImplementedError()  # pragma: no cover


def _launches_new_checkers() -> None:
    """Launch new checkers."""
    raise NotImplementedError()  # pragma: no cover
