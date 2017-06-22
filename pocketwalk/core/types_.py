# coding: utf-8


"""Pocketwalk internal types."""


# [ Imports ]
import enum


# [ API ]
class Result(enum.Enum):
    """Result enums."""

    PASS = enum.auto()
    FAIL = enum.auto()
    EXIT = enum.auto()


class Command(enum.Enum):
    """Command enums."""

    EXIT = enum.auto()
