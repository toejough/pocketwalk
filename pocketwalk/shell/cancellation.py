#! /usr/bin/env python
# coding: utf-8


"""Pocketwalk Cancellation Interface."""


# [ Imports ]
import abc


# [ API ]
class Cancellation(abc.ABC):
    """Cancellation plugin ABC."""

    @abc.abstractmethod
    def __init__(self):
        """Init the state."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def cancelled(self):
        """Return whether or not the application has been cancelled."""
        raise NotImplementedError
