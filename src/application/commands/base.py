"""Base command class for the command pattern."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


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
        self.timestamp = datetime.now()
        self._executed = False
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command.
        
        Should modify domain state and set _executed = True.
        """
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command.
        
        Should restore domain state to pre-execution state.
        """
        pass
    
    def is_executed(self) -> bool:
        """Check if command has been executed."""
        return self._executed
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.description!r})"
