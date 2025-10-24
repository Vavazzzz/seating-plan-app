# src/utils/json_io.py
from PyQt6.QtWidgets import QFileDialog
from pathlib import Path
from typing import Optional
from ..models.seating_plan import SeatingPlan

_last_dir: Path | None = None  # remembers last used folder

def _get_suggested_filename(seating_plan: SeatingPlan) -> str:
    """Generate a filename suggestion based on plan content."""
    if seating_plan.sections:
        first_section = next(iter(seating_plan.sections.values()))
        # derive a name from the first section (e.g., "Section A" -> "section_a.json")
        base_name = first_section.name.lower().replace(" ", "_")
        return f"{base_name}_plan.json"
    return "seating_plan.json"

def import_json_dialog(parent) -> Optional[SeatingPlan]:
    global _last_dir
    start_dir = str(_last_dir) if _last_dir else ""
    path, _ = QFileDialog.getOpenFileName(
        parent,
        "Import seating plan JSON",
        start_dir,
        "JSON Files (*.json);;All Files (*)"
    )
    if path:
        sp = SeatingPlan()
        sp.import_from_json(path)
        _last_dir = Path(path).parent
        return sp
    return None

def export_json_dialog(parent, seating_plan: SeatingPlan):
    global _last_dir
    start_dir = str(_last_dir) if _last_dir else ""
    suggested_name = _get_suggested_filename(seating_plan)
    path, _ = QFileDialog.getSaveFileName(
        parent,
        "Export seating plan JSON",
        str(Path(start_dir) / suggested_name),
        "JSON Files (*.json);;All Files (*)"
    )
    if not path:
        return

    # ensure .json extension
    if not path.lower().endswith(".json"):
        path += ".json"

    seating_plan.export_to_json(path)
    _last_dir = Path(path).parent
