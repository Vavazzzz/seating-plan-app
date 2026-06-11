"""Base command class for the command pattern."""

from abc import ABC, abstractmethod


class Command(ABC):
    """Abstract base class for all commands.

    Commands represent user actions that modify domain state.
    They support undo/redo by implementing execute() and undo().
    """

    def __init__(self, description: str = ""):
        """Initialize command with optional description.

        Args:
            description: Human-readable description of this command
        """
        self.description = description

    @abstractmethod
    def execute(self) -> None:
        """Execute the command, snapshotting any state needed by undo()."""
        pass

    @abstractmethod
    def undo(self) -> None:
        """Undo the command by replaying the state captured in execute()."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.description!r})"
