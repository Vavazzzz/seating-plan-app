"""Abstract repository interface for seating plan persistence."""

from abc import ABC, abstractmethod
from pathlib import Path

from ...domain.models.seating_plan import SeatingPlan


class SeatingPlanRepository(ABC):
    """Abstract base class for seating plan persistence."""
    
    @abstractmethod
    def save(self, seating_plan: SeatingPlan, file_path: str) -> None:
        """Save a seating plan to a file.
        
        Args:
            seating_plan: The SeatingPlan to save
            file_path: Where to save the file
        """
        pass
    
    @abstractmethod
    def load(self, file_path: str) -> SeatingPlan:
        """Load a seating plan from a file.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            The loaded SeatingPlan
        """
        pass
