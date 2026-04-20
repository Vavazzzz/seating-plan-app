"""Base service class for domain operations coordination."""

from typing import TYPE_CHECKING, Callable, Optional, List
from ..result import Result, ValidationErrors
from ..handlers.command_handler import CommandHandler

if TYPE_CHECKING:
    from domain.models.seating_plan import SeatingPlan


class BaseService:
    """Base service providing common functionality for domain services.
    
    Coordinates command execution, validation, and error handling.
    """
    
    def __init__(self, seating_plan: "SeatingPlan", command_handler: CommandHandler):
        """Initialize the service.
        
        Args:
            seating_plan: The seating plan to operate on
            command_handler: Handler for undo/redo operations
        """
        self.seating_plan = seating_plan
        self.command_handler = command_handler
        self._validation_errors: Optional[ValidationErrors] = None
    
    def validate(self, condition: bool, error_message: str) -> None:
        """Add a validation error for later retrieval.
        
        Args:
            condition: Should be True if valid (error added if False)
            error_message: Description of the validation error
        """
        if not condition:
            if self._validation_errors is None:
                self._validation_errors = ValidationErrors()
            self._validation_errors.add(error_message)
    
    def get_validation_errors(self) -> ValidationErrors:
        """Get collected validation errors.
        
        Returns:
            ValidationErrors object (may be empty)
        """
        if self._validation_errors is None:
            return ValidationErrors()
        return self._validation_errors
    
    def clear_validation_errors(self) -> None:
        """Clear collected validation errors."""
        self._validation_errors = None
    
    def has_validation_errors(self) -> bool:
        """Check if there are any validation errors."""
        return self._validation_errors is not None and self._validation_errors.has_errors()
    
    def validation_errors_as_result(self) -> Result[None, ValidationErrors]:
        """Convert validation errors to a Result.
        
        Returns:
            Result.failure() if errors exist, Result.success() otherwise
        """
        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())
        return Result.success(None)
    
    def add_error_callback(self, callback: Callable[[str], None]) -> None:
        """Add a callback for command errors.
        
        Args:
            callback: Function to call with error message
        """
        self.command_handler.on_command_executed = callback
