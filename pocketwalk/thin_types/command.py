# coding: utf-8


"""Command."""


# [ API ]
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
