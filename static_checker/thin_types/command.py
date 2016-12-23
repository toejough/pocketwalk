"""Command."""


# [ Imports ]
import logging


# [ Logging ]
logger = logging.getLogger(__name__)


# [ API ]
# XXX Better doc strings
# XXX add unit tests
class Command:
    """Command."""

    def __init__(
        self,
        command: str,
        *args: str
    ) -> None:
        """Init the state."""
        self.command = command
        self.args = args
