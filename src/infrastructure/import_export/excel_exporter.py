"""Excel format exporter for seating plans."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.models.seating_plan import SeatingPlan

from openpyxl import Workbook

from domain.exceptions import SeatingPlanException
from infrastructure.utils.alphanum_handler import alphanum_sort_key
from .abstract import Exporter


class ExcelExporter(Exporter):
    """Export seating plans to Excel (.xlsx) files."""
    
    SUPPORTED_EXTENSIONS = (".xlsx",)
    
    def supports(self, file_path: str) -> bool:
        """Check if this exporter handles the file type."""
        return file_path.lower().endswith(self.SUPPORTED_EXTENSIONS)
    
    def export_seating_plan(self, file_path: str, seating_plan: "SeatingPlan") -> None:
        """Export a seating plan to an Excel file.
        
        Excel format:
        - Columns: section, rows, seats, secnam, capacity, type
        - type: 0 = numbered seats, non-zero = general admission
        
        Args:
            file_path: Path where the Excel file will be saved
            seating_plan: The SeatingPlan to export
            
        Raises:
            SeatingPlanException: If export fails
        """
        try:
            file_path_obj = Path(file_path)
            
            # Ensure directory exists
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Create workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Seating Plan"
            
            # Write headers
            ws.append(["section", "rows", "seats", "secnam", "capacity", "type"])
            
            # Write section data
            for section in seating_plan.sections.values():
                if section.is_ga:
                    # General admission section
                    ws.append([section.name, "", "", section.name, "1", 1])
                else:
                    # Numbered seats: organize by row
                    rows = {}
                    for seat in section.seats.values():
                        rows.setdefault(seat.row_number, []).append(str(seat.seat_number))
                    
                    for row_number in sorted(rows.keys(), key=alphanum_sort_key):
                        seat_list = rows[row_number]
                        # Sort seats within each row
                        seat_list_sorted = sorted(seat_list, key=alphanum_sort_key)
                        
                        ws.append([
                            section.name,
                            row_number,
                            ",".join(seat_list_sorted),
                            section.name,
                            "",
                            0
                        ])
            
            # Save workbook
            wb.save(str(file_path_obj))
            
        except IOError as e:
            raise SeatingPlanException(
                f"Failed to write Excel file: {e}",
                error_code="FILE_WRITE_FAILED"
            ) from e
        except Exception as e:
            raise SeatingPlanException(
                f"Failed to export to Excel: {e}",
                error_code="EXPORT_FAILED"
            ) from e
