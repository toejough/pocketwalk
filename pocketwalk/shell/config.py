#! /usr/bin/env python
# coding: utf-8


"""Pocketwalk config interface."""


# [ Imports ]
import abc


# [ API ]
class Config(abc.ABC):
    """Config plugin for pocketwalk."""

    # [ API ]
    @staticmethod
    @abc.abstractmethod
    async def get_tools(config):
        """Return tools from the config."""
        raise NotImplementedError

    @abc.abstractmethod
    async def loop_forever(self):
        """Return whether to loop forever."""
        raise NotImplementedError

    @abc.abstractmethod
    async def loop_till_pass(self):
        """Return whether to loop till pass."""
        raise NotImplementedError

    @abc.abstractmethod
    async def get_config(self):
        """Get the config."""
        raise NotImplementedError
