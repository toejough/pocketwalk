"""CLI args."""


# [ Imports ]
# [ -Python ]
import logging
from typing import Any
from argparse import ArgumentParser
# [ -Third Party ]
import a_sync
# [ -Project ]
from ..thin_types.real_file_path import real_file_path


# [ Logging ]
logger = logging.getLogger(__name__)


# XXX Better doc strings
# XXX match globs and directories
# [ Helpers ]
def get_parser() -> ArgumentParser:
    """Get arg parser."""
    parser = ArgumentParser()
    parser.add_argument(
        '-c', '--config',
        help="Path to the yaml config file to use. [default: %(default)s]",
        type=real_file_path,
        default='check.yaml'
    )
    parser.add_argument(
        '-1', '--once',
        help="Only run the checks once [default: False]",
        action='store_true'
    )
    return parser


# [ API ]
async def get_arg(arg: str) -> Any:
    """Return the arg."""
    parser = get_parser()
    try:
        args = await a_sync.run(parser.parse_args)
    except Exception as e:
        # XXX mypy says this is incompatible - it is not.
        parser.error(e)  # type: ignore
    return getattr(args, arg)
