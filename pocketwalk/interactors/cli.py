# coding: utf-8


"""CLI args."""


# [ Imports ]
# [ -Python ]
from argparse import ArgumentParser
from typing import Any
# [ -Third Party ]
import a_sync
# [ -Project ]
from ..thin_types.real_file_path import real_file_path


# [ Helpers ]
def get_parser() -> ArgumentParser:
    """Get arg parser."""
    parser = ArgumentParser()
    parser.add_argument(
        '-c', '--config',
        help="Path to the yaml config file to use. [default: %(default)s]",
        type=real_file_path,
        default='check.yaml',
    )
    parser.add_argument(
        '-1', '--once',
        help="Only run the checks once [default: False]",
        action='store_true',
    )
    return parser


# [ API ]
async def get_arg(arg: str) -> Any:
    """Return the arg."""
    parser = get_parser()
    try:
        args = await a_sync.run(parser.parse_args)
    except Exception as e:
        # mypy says this is incompatible - it is not.
        parser.error(e)  # type: ignore
    return getattr(args, arg)
