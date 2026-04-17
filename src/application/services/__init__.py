"""Application services layer.

Provides high-level, validated operations on the seating plan.
All service methods return Result types for explicit error handling.
Services coordinate with CommandHandler for undo/redo functionality.
"""

from .base import BaseService
from .seating_plan_service import SeatingPlanService
from .section_service import SectionService
from .seat_service import SeatService

__all__ = [
    "BaseService",
    "SeatingPlanService",
    "SectionService",
    "SeatService",
]
