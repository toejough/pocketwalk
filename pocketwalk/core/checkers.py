# coding: utf-8


"""Checker logic for pocketwalk."""


# [ Import ]
# [ -Python ]
import enum
import typing
# [ -Third Party ]
from runaway import extras, signals


# [ API ]
class Result(enum.Enum):
    """Result enums."""

    RUNNING = enum.auto()
    ALL_PASSING = enum.auto()


class WatchResult(enum.Enum):
    """WatchResult enums."""

    CHANGED = enum.auto()


async def run_until_all_pass() -> None:
    """Run the checkers until they all pass."""
    await signals.call(extras.do_while, _not_all_passing, _run_single, None)


def watch_until_change() -> WatchResult:
    """Run the watchers until a change."""
    raise NotImplementedError  # pragma: no cover


# [ Internals ]
async def _run_single(_state: typing.Any) -> typing.Any:
    """Run a single iteration of checker actions."""
    await signals.call(_get_checker_list)
    await signals.call(_cancel_removed_checkers)
    await signals.call(_launch_new_checkers)
    await signals.call(_relaunch_changed_checkers)
    await signals.call(_launch_watchers_for_completed_checkers)
    await signals.call(_launch_watcher_for_checker_list)
    await signals.call(_wait_for_any_future)
    checker_state = await signals.call(_analyze_checker_state)
    if checker_state is Result.ALL_PASSING:
        await signals.call(_cancel_all_futures)
    return checker_state


def _not_all_passing(state: typing.Any) -> bool:
    """Test whether or not to continue the loop."""
    return state is not Result.ALL_PASSING


def _get_checker_list() -> list:
    """Return the checker list."""
    raise NotImplementedError()  # pragma: no cover


async def _cancel_removed_checkers(removed_checkers: list) -> None:
    """Cancel the removed checkers."""
    await signals.call(extras.do_while, _checkers_to_cancel, _cancel_single, removed_checkers)


def _checkers_to_cancel(state: list) -> bool:
    """Test whether or not to continue the loop."""
    raise NotImplementedError(state)  # pragma: no cover


def _launch_new_checkers() -> None:
    """Launch new checkers."""
    raise NotImplementedError()  # pragma: no cover


def _relaunch_changed_checkers() -> None:
    """Relaunch changed checkers."""
    raise NotImplementedError()  # pragma: no cover


def _launch_watchers_for_completed_checkers() -> None:
    """Launch watchers for completed checkers."""
    raise NotImplementedError()  # pragma: no cover


def _launch_watcher_for_checker_list() -> None:
    """Launch watcher for checker list."""
    raise NotImplementedError()  # pragma: no cover


def _analyze_checker_state() -> None:
    """Analyze the checker state for the current status."""
    raise NotImplementedError()  # pragma: no cover


def _wait_for_any_future() -> None:
    """Wait for any future."""
    raise NotImplementedError()  # pragma: no cover


def _cancel_all_futures() -> None:
    """Cancel all futures."""
    raise NotImplementedError()  # pragma: no cover


async def _cancel_single() -> None:
    """Cancel a removed checker."""
    raise NotImplementedError()  # pragma: no cover
