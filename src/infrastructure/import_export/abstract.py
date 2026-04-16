"""Abstract base classes for import/export infrastructure."""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.models.seating_plan import SeatingPlan


class Importer(ABC):
    """Abstract base class for seating plan importers."""
    
    @abstractmethod
    def supports(self, file_path: str) -> bool:
        """Check if this importer can handle the given file type.
        
        Args:
            file_path: Path to the file to import
            
        Returns:
            True if this importer can handle the file, False otherwise
        """
        pass
    
    @abstractmethod
    def import_seating_plan(self, file_path: str, plan_name: str) -> "SeatingPlan":
        """Import a seating plan from the given file.
        
        Args:
            file_path: Path to the file to import
            plan_name: Name to assign to the imported plan
            
        Returns:
            A new SeatingPlan instance populated from the file
            
        Raises:
            ImportException: If the import fails
        """
        pass


class Exporter(ABC):
    """Abstract base class for seating plan exporters."""
    
    @abstractmethod
    def supports(self, file_path: str) -> bool:
        """Check if this exporter can handle the given file type.
        
        Args:
            file_path: Path to the file to export to
            
        Returns:
            True if this exporter can handle the file, False otherwise
        """
        pass
    
    @abstractmethod
    def export_seating_plan(self, file_path: str, seating_plan: "SeatingPlan") -> None:
        """Export a seating plan to the given file.
        
        Args:
            file_path: Path to export to
            seating_plan: The SeatingPlan to export
            
        Raises:
            ExportException: If the export fails
        """
        pass
