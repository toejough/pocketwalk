# coding: utf-8


"""Checker logic for pocketwalk."""


# [ Import ]
# [ -Python ]
import enum
# [ -Third Party ]
# from runaway import extras, signals
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


def run() -> Result:
    """Run the checkers."""
    raise NotImplementedError  # pragma: no cover


def watch() -> WatchResult:
    """Run the watchers."""
    raise NotImplementedError  # pragma: no cover


# async def loop() -> Result:
#     """Run the static checkers concurrently."""
#     # mypy says this returns any...technically true?
#     return await signals.call(extras.do_while, _loop_predicate, _run_single, None)  # type: ignore


# def watch() -> WatchResult:
#     """Watch the static checker files concurrently."""
#     return WatchResult.CHANGED


# # [ Internals ]
# def _run_single() -> Result:
#     """Run a single iteration of checker actions."""
#     raise NotImplementedError


# def _loop_predicate() -> bool:
#     """Test whether or not to continue the loop."""
#     raise NotImplementedError
