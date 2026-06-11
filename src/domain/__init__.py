"""Domain layer - models, utilities, and exceptions."""

from .models import SeatingPlan, Section, Seat
from .exceptions import (
    SeatingPlanException,
    ValidationError,
    MergeConflictError,
)

__all__ = [
    "SeatingPlan",
    "Section",
    "Seat",
    "SeatingPlanException",
    "ValidationError",
    "MergeConflictError",
]
