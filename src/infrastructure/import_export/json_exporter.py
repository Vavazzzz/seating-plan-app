"""JSON format exporter for seating plans."""

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.models.seating_plan import SeatingPlan

from domain.exceptions import SeatingPlanException
from .abstract import Exporter


class JSONExporter(Exporter):
    """Export seating plans to JSON (.json, .seatproj) files."""
    
    SUPPORTED_EXTENSIONS = (".json", ".seatproj")
    
    def supports(self, file_path: str) -> bool:
        """Check if this exporter handles the file type."""
        return file_path.lower().endswith(self.SUPPORTED_EXTENSIONS)
    
    def export_seating_plan(self, file_path: str, seating_plan: "SeatingPlan") -> None:
        """Export a seating plan to a JSON file.
        
        Args:
            file_path: Path where the JSON file will be saved
            seating_plan: The SeatingPlan to export
            
        Raises:
            SeatingPlanException: If export fails
        """
        try:
            file_path_obj = Path(file_path)
            
            # Ensure directory exists
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dictionary
            data = seating_plan.to_dict()
            
            # Write JSON
            with open(file_path_obj, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
        except IOError as e:
            raise SeatingPlanException(
                f"Failed to write JSON file: {e}",
                error_code="FILE_WRITE_FAILED"
            ) from e
        except Exception as e:
            raise SeatingPlanException(
                f"Failed to export to JSON: {e}",
                error_code="EXPORT_FAILED"
            ) from e
