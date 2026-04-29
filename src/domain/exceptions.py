"""Domain-specific exceptions for the seating plan application."""

from typing import List, Optional


class SeatingPlanException(Exception):
    """Base exception for all seating plan domain errors."""
    
    def __init__(self, message: str, error_code: str = "UNKNOWN") -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class ValidationError(SeatingPlanException):
    """Raised when domain validation fails."""
    
    def __init__(self, message: str, errors: Optional[List[str]] = None) -> None:
        super().__init__(message, "VALIDATION_ERROR")
        self.errors = errors or [message]


class MergeConflictError(SeatingPlanException):
    """Raised when attempting to merge sections that contain conflicting seats."""
    
    def __init__(self, message: str, conflicts: Optional[dict] = None) -> None:
        super().__init__(message, "MERGE_CONFLICT")
        self.conflicts = conflicts or {}


class SectionNotFoundError(SeatingPlanException):
    """Raised when a section is not found."""
    
    def __init__(self, section_name: str) -> None:
        message = f"Section '{section_name}' not found"
        super().__init__(message, "SECTION_NOT_FOUND")
        self.section_name = section_name


class DuplicateNameError(SeatingPlanException):
    """Raised when attempting to create a duplicate name."""
    
    def __init__(self, entity_type: str, name: str) -> None:
        message = f"{entity_type} with name '{name}' already exists"
        super().__init__(message, "DUPLICATE_NAME")
        self.name = name


class InvalidStateError(SeatingPlanException):
    """Raised when an operation is attempted in an invalid state."""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, "INVALID_STATE")
