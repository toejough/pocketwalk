#! /usr/bin/env python
# coding: utf-8


"""Pocketwalk config."""


# [ Imports ]
# [ -Python ]
import argparse
import pathlib
# [ -Third Party ]
import pytoml as toml


# [ API ]
# XXX [ config ] need to show config on change
# XXX [ config ] need a save config option (not saved)
# XXX [ config ] need a config-path option (not saved)
# XXX need an option to error on certain output patterns
# XXX need an option to strip output patterns, and ignore error if no output left
# XXX need an option to warn if there are unused ignores
def get_config():
    """Get the config plugin."""
    return Config()


# [ API ]
class Config:
    """Config plugin for pocketwalk."""

    # [ API ]
    @staticmethod
    async def get_tools(config):
        """Return tools from the config."""
        return config['tools']

    async def loop_forever(self):
        """Return whether to loop forever."""
        return (await self._get_config()).run == 'forever'

    async def loop_till_pass(self):
        """Return whether to loop till pass."""
        return (await self._get_config()).run == 'till-pass'

    async def get_config(self):
        """Get the config."""
        config = await self._get_config()
        config_dict = vars(config)
        for tool in config.tools:
            config_dict[f'{tool}_targets'] = self._glob_paths(config_dict[f'{tool}_targets'])
            config_dict[f'{tool}_triggers'] = self._glob_paths(config_dict[f'{tool}_triggers'])
            config_dict[f'{tool}_args'] = self._glob_paths(config_dict[f'{tool}_args'])
        config_dict['config_path'] = self._get_path()
        return config_dict

    # [ Internals ]
    @staticmethod
    def _get_path():
        """Get the config path."""
        return ".pocketwalk.toml"

    @staticmethod
    def _glob_paths(args):
        """Expand globbed paths in the args."""
        if not isinstance(args, list):
            args = args.split()
        unglobbed = []
        for this_arg in args:
            if '*' in this_arg:
                if this_arg.startswith('/'):
                    unglobbed += [str(p) for p in pathlib.Path('/').glob(this_arg[1:])]
                else:
                    unglobbed += [str(p) for p in pathlib.Path.cwd().glob(this_arg)]
            else:
                unglobbed.append(this_arg)
        return unglobbed

    async def _get_config(self):
        """Get the actual config."""
        config_file = pathlib.Path.cwd() / '.pocketwalk.toml'
        config_string = config_file.read_text()  # pylint: disable=no-member
        defaults = toml.loads(config_string)

        tool_parser = argparse.ArgumentParser(add_help=False)
        tool_parser.add_argument(
            '--run',
            help="How long to run and loop pocketwalk. [default: %(default)s]",
            choices=['forever', 'till-pass', 'once'],
            default=defaults['run'],
        )
        tool_parser.add_argument(
            '--tools',
            help="Tools to run. [default: %(default)s]",
            metavar='EXECUTABLE',
            default=list(defaults.get('tools', {}).keys()),
            nargs='*',
        )
        tool_parser.add_argument(
            '--no-vcs',
            help="Disable VCS.",
            action='store_true',
        )
        args, _unknown = tool_parser.parse_known_args()

        parser = argparse.ArgumentParser(parents=[tool_parser])
        for tool in args.tools:
            parser.add_argument(
                f'--{tool}-targets',
                help=f"Target files for {tool} to run against. [default: %(default)s]",
                metavar='PATH',
                default=self._glob_paths(defaults.get('tools', {}).get(tool, {}).get('target_paths', [])),
                nargs='+',
            )
            parser.add_argument(
                f'--{tool}-triggers',
                help=f"Trigger files for {tool} to run against. [default: %(default)s]",
                metavar='PATH',
                default=self._glob_paths(defaults.get('tools', {}).get(tool, {}).get('trigger_paths', [])),
                nargs='*',
            )
            parser.add_argument(
                f'--{tool}-preconditions',
                help=f"Tools to pass before {tool} can be run. [default: %(default)s]",
                metavar='TOOL',
                default=defaults.get('tools', {}).get(tool, {}).get('preconditions', []),
                nargs='*',
            )
            parser.add_argument(
                f'--{tool}-args',
                help=(
                    f"Args to pass {tool}, in python string format." +
                    f"  The template '{{target_paths}}' will get replaced at runtime with the target paths," +
                    f"  '{{affected_paths}}' will get replaced with affected paths." +
                    f"  [default: %(default)s]"
                ),
                metavar='STRING',
                default=self._glob_paths(defaults.get('tools', {}).get(tool, {}).get('config', "")),
            )

        return parser.parse_args()
