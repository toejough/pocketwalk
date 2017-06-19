# coding: utf-8


"""Pocketwalk internal types."""


# [ Imports ]
import enum


# [ API ]
class Result(enum.Enum):
    """Result enums."""

    PASS = enum.auto()
    FAIL = enum.auto()
