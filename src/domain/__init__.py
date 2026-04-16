"""Domain layer - models, services, and exceptions."""

from .models import SeatingPlan, Section, Seat
from .exceptions import (
    SeatingPlanException,
    ValidationError,
    MergeConflictError,
    SectionNotFoundError,
    DuplicateNameError,
    InvalidStateError,
)

__all__ = [
    "SeatingPlan",
    "Section",
    "Seat",
    "SeatingPlanException",
    "ValidationError",
    "MergeConflictError",
    "SectionNotFoundError",
    "DuplicateNameError",
    "InvalidStateError",
]
