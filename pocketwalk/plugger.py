#! /usr/bin/env python
# coding: utf-8


"""Pocketwalk plugin lib."""


# [ Imports ]
import pkg_resources


# [ API ]
# XXX validate function signatures & raise an exception if the chosen plugin doesn't match.
# XXX validate function typing & raise if the chosen plugin doesn't match.
# XXX allow multiple plugins for things that can just be called in parallel
# XXX supply a default conflict resolver, and allow overrides
class Plugger:
    """Plugin management tool."""

    def __init__(self, namespace):
        """Init the state."""
        self._namespace = namespace

    # [ API ]
    def resolve(self, target):
        """
        Resolve the plugin for the given target.

        Plugins will be discovered/loaded via setuptools entry points.
        The namespace for the entry points will be {init-namespace}_{target-name},
        all lower-cased.

        The function/class the plugin resolves to will be called with no arguments.
        """
        plugins = {}
        namespace = f'{self._namespace.lower()}_{target.__name__.lower()}'
        print(f"Loading plugins for {namespace}...")
        for entry_point in pkg_resources.iter_entry_points(namespace):
            print(f"  {entry_point.name}")
            plugins[entry_point.name] = entry_point.load()()

        num_plugins = len(plugins)
        if 1 < num_plugins:
            raise RuntimeError(f"Too many ({num_plugins}) plugins for {namespace}.")
        if not num_plugins:
            raise RuntimeError(f"No plugins found for {namespace}")

        return list(plugins.values())[0]
