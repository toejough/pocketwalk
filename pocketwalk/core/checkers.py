# coding: utf-8


"""Checker logic for pocketwalk."""


# [ Import ]
# [ -Python ]
import enum
# [ -Project ]
from pocketwalk.core.types_ import Result


# [ Internals ]
class WatchResult(enum.Enum):
    """WatchResult enums."""

    CHANGED = enum.auto()


# [ API ]
def run() -> Result:
    """Run the static checkers concurrently."""
    return Result.PASS


def watch() -> WatchResult:
    """Watch the static checker files concurrently."""
    return WatchResult.CHANGED
