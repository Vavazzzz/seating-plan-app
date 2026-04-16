"""JSON format importer for seating plans."""

import json
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.models.seating_plan import SeatingPlan

from ...domain.exceptions import SeatingPlanException
from .abstract import Importer


class JSONImporter(Importer):
    """Import seating plans from JSON (.json, .seatproj) files."""
    
    SUPPORTED_EXTENSIONS = (".json", ".seatproj")
    
    def supports(self, file_path: str) -> bool:
        """Check if this importer handles the file type."""
        return file_path.lower().endswith(self.SUPPORTED_EXTENSIONS)
    
    def import_seating_plan(self, file_path: str, plan_name: str) -> "SeatingPlan":
        """Import a seating plan from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            plan_name: Name for the imported seating plan
            
        Returns:
            A populated SeatingPlan instance
            
        Raises:
            SeatingPlanException: If import fails
        """
        try:
            from ...domain.models.seating_plan import SeatingPlan
            
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                raise SeatingPlanException(
                    f"File not found: {file_path}",
                    error_code="FILE_NOT_FOUND"
                )
            
            with open(file_path_obj, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Create seating plan with provided name
            seating_plan = SeatingPlan(plan_name or "Imported Plan")
            
            # Populate from JSON data
            seating_plan.from_dict(data)
            
            return seating_plan
            
        except json.JSONDecodeError as e:
            raise SeatingPlanException(
                f"Invalid JSON format: {e}",
                error_code="INVALID_JSON"
            ) from e
        except KeyError as e:
            raise SeatingPlanException(
                f"Missing required field in JSON: {e}",
                error_code="MISSING_FIELD"
            ) from e
        except Exception as e:
            raise SeatingPlanException(
                f"Failed to import JSON: {e}",
                error_code="IMPORT_FAILED"
            ) from e
