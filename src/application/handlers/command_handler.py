"""Command handler for managing command execution and undo/redo."""

from typing import List, Optional, Callable
from ..commands.base import Command


class CommandHandler:
    """Manages command execution, undo/redo history.
    
    Maintains undo and redo stacks for granular command-based undo/redo.
    """
    
    def __init__(self, max_history: int = 100):
        """Initialize command handler.
        
        Args:
            max_history: Maximum number of commands to keep in history
        """
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []
        self.max_history = max_history
        
        # Optional callbacks for UI notifications
        self.on_command_executed: Optional[Callable[[Command], None]] = None
        self.on_command_undone: Optional[Callable[[Command], None]] = None
        self.on_command_redone: Optional[Callable[[Command], None]] = None
    
    def execute(self, command: Command) -> None:
        """Execute a command and store it for undo.
        
        Executing a command clears the redo stack (new action branch).
        
        Args:
            command: The Command to execute
        """
        command.execute()
        self.undo_stack.append(command)
        
        # Limit history size
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        
        # Clear redo stack (new action branch)
        self.redo_stack.clear()
        
        # Notify listeners
        if self.on_command_executed:
            self.on_command_executed(command)
    
    def undo(self) -> bool:
        """Undo the last command if possible.
        
        Returns:
            True if undo was performed, False if nothing to undo
        """
        if not self.undo_stack:
            return False
        
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        
        # Notify listeners
        if self.on_command_undone:
            self.on_command_undone(command)
        
        return True
    
    def redo(self) -> bool:
        """Redo the last undone command if possible.
        
        Returns:
            True if redo was performed, False if nothing to redo
        """
        if not self.redo_stack:
            return False
        
        command = self.redo_stack.pop()
        command.execute()
        self.undo_stack.append(command)
        
        # Notify listeners
        if self.on_command_redone:
            self.on_command_redone(command)
        
        return True
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self.redo_stack) > 0
    
    def get_undo_description(self) -> Optional[str]:
        """Get description of next undo action."""
        if self.undo_stack:
            return self.undo_stack[-1].description
        return None
    
    def get_redo_description(self) -> Optional[str]:
        """Get description of next redo action."""
        if self.redo_stack:
            return self.redo_stack[-1].description
        return None
    
    def clear_history(self) -> None:
        """Clear all undo/redo history."""
        self.undo_stack.clear()
        self.redo_stack.clear()
    
    def get_history_summary(self) -> str:
        """Get summary of command history."""
        undo_cmds = ", ".join([cmd.description for cmd in self.undo_stack[-5:]])
        redo_cmds = ", ".join([cmd.description for cmd in self.redo_stack[-5:]])
        return f"Undo: [{undo_cmds}], Redo: [{redo_cmds}]"
