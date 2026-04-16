"""JSON-based repository for seating plan persistence."""

from pathlib import Path

from ...domain.models.seating_plan import SeatingPlan
from ...domain.exceptions import SeatingPlanException
from ..import_export import JSONImporter, JSONExporter
from .abstract import SeatingPlanRepository


class JSONRepository(SeatingPlanRepository):
    """Save and load seating plans using JSON format."""
    
    def __init__(self):
        self.importer = JSONImporter()
        self.exporter = JSONExporter()
    
    def save(self, seating_plan: SeatingPlan, file_path: str) -> None:
        """Save a seating plan to a JSON file.
        
        Args:
            seating_plan: The SeatingPlan to save
            file_path: Path to save to (should end in .json or .seatproj)
            
        Raises:
            SeatingPlanException: If save fails
        """
        self.exporter.export_seating_plan(file_path, seating_plan)
    
    def load(self, file_path: str) -> SeatingPlan:
        """Load a seating plan from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            The loaded SeatingPlan
            
        Raises:
            SeatingPlanException: If load fails
        """
        plan_name = Path(file_path).stem
        return self.importer.import_seating_plan(file_path, plan_name)
