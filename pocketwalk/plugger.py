#! /usr/bin/env python
# coding: utf-8


"""Pocketwalk plugin lib."""


# [ Imports ]
import inspect
import pkg_resources


# [ API ]
# XXX need per function docs
# XXX need project docs
# XXX need mypy typing
# XXX figure out how to specify plugins & order discovered
#     function providers deterministically.
#     perhaps a config file with white/black lists?
class Plugger:
    """Plugin management tool."""

    @staticmethod
    def get_plugins(namespace):
        """Get plugins."""
        plugins = {}
        print(f"Loading plugins for {namespace}...")
        for entry_point in pkg_resources.iter_entry_points(namespace):
            print(f"  {entry_point.name}")
            plugins[entry_point.name] = entry_point.load()()
        return plugins

    @staticmethod
    def get_functions(obj):
        """Get functions to plug from the shell."""
        funcs = dict(inspect.getmembers(obj, callable))
        public_funcs = {k: v for k, v in funcs.items() if not k.startswith('_')}
        return public_funcs

    @staticmethod
    def plug(obj, *, name, replacement):
        """Plug a replacement into the object."""
        current_func = getattr(obj, name)
        is_multi_ = getattr(current_func, 'multi', False)
        if is_multi_:
            funcs = current_func.funcs
            funcs.append(replacement)
            # XXX need async/sync detection for original and plugins

            async def multi_replacement(*args, **kwargs):
                """A multi-replacement function."""
                for this_func in funcs:
                    await this_func(*args, **kwargs)
            replacement = multi_replacement
            replacement.multi = is_multi_
            replacement.funcs = funcs
        setattr(obj, name, replacement)

    @staticmethod
    def is_multi(obj, *, name):
        """Plug a replacement into the object."""
        current_func = getattr(obj, name)
        return getattr(current_func, 'multi', False)

    def implement(self, obj, namespace):
        """Implement the object with plugins from the given namespace."""
        plugins = self.get_plugins(namespace)
        functions = self.get_functions(obj)
        for func_name in functions:
            matched = False
            for plugin in plugins.values():
                plugin_functions = self.get_functions(plugin)
                if func_name in plugin_functions:
                    self.plug(obj, name=func_name, replacement=plugin_functions[func_name])
                    matched = True
                    if not self.is_multi(obj, name=func_name):
                        break
            if not matched:
                raise RuntimeError(f"no plugin found to implement {func_name} for {obj}")
        return obj


def multi(wrapped):
    """Decorate the wrapped function as a multi-plugin."""
    wrapped.multi = True
    wrapped.funcs = []
    return wrapped


# FOO_PASSWORD = "abcdefg"
