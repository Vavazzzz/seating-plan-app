"""Avail XML format importer for seating plans."""

from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from domain.models.seating_plan import SeatingPlan

from bs4 import BeautifulSoup

from domain.exceptions import SeatingPlanException
from .abstract import Importer


class AvailImporter(Importer):
    """Import seating plans from Avail XML (.xml) files."""
    
    SUPPORTED_EXTENSIONS = (".xml",)
    
    def supports(self, file_path: str) -> bool:
        """Check if this importer handles the file type."""
        return file_path.lower().endswith(self.SUPPORTED_EXTENSIONS)
    
    def import_seating_plan(self, file_path: str, plan_name: str) -> "SeatingPlan":
        """Import a seating plan from an Avail XML file.
        
        Expected XML structure:
        <section_id_list>
          <e>
            <section_id>...</section_id>
            <section_name>...</section_name>
            <is_ga>true|false</is_ga>
            <row_names>
              <e>row1</e>
              <e>row2</e>
            </row_names>
            <seat_names>
              <e>A</e>
              <e>B</e>
            </seat_names>
          </e>
        </section_id_list>
        
        Args:
            file_path: Path to the Avail XML file
            plan_name: Name for the imported seating plan
            
        Returns:
            A populated SeatingPlan instance
            
        Raises:
            SeatingPlanException: If import fails
        """
        try:
            from domain.models.seating_plan import SeatingPlan
            
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                raise SeatingPlanException(
                    f"File not found: {file_path}",
                    error_code="FILE_NOT_FOUND"
                )
            
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse XML
            soup = BeautifulSoup(content, 'lxml')
            section_id_list = soup.find('section_id_list')
            
            if not section_id_list:
                raise SeatingPlanException(
                    "No 'section_id_list' element found in XML",
                    error_code="INVALID_XML_STRUCTURE"
                )
            
            # Create seating plan
            seating_plan = SeatingPlan(plan_name or "Imported Plan")
            
            # Parse sections
            for section_elem in section_id_list.find_all('e'):
                try:
                    section_id_tag = section_elem.find('section_id')
                    if not section_id_tag:
                        continue  # Skip entries without section_id
                    
                    section_name_tag = section_elem.find('section_name')
                    is_ga_tag = section_elem.find('is_ga')
                    
                    if not section_name_tag or not is_ga_tag:
                        continue  # Skip incomplete entries
                    
                    section_name = section_name_tag.text.strip()
                    is_ga = is_ga_tag.text.lower() == 'true'
                    
                    # Create section
                    if section_name not in seating_plan.sections:
                        seating_plan.add_section(section_name, is_ga=is_ga)
                    
                    # Add seats for non-GA sections
                    if not is_ga:
                        row_names_elem = section_elem.find('row_names')
                        seat_names_elem = section_elem.find('seat_names')
                        
                        if row_names_elem and seat_names_elem:
                            row_names = [
                                r.text.strip() 
                                for r in row_names_elem.find_all('e')
                            ]
                            seat_names = [
                                s.text.strip() 
                                for s in seat_names_elem.find_all('e')
                            ]
                            
                            for row in row_names:
                                for seat in seat_names:
                                    seating_plan.sections[section_name].add_seat(row, seat)
                
                except Exception as e:
                    raise SeatingPlanException(
                        f"Error parsing section element: {e}",
                        error_code="XML_PARSE_ERROR"
                    ) from e
            
            return seating_plan
            
        except SeatingPlanException:
            raise
        except Exception as e:
            raise SeatingPlanException(
                f"Failed to import Avail XML: {e}",
                error_code="IMPORT_FAILED"
            ) from e
