from PyQt6.QtWidgets import QFileDialog, QMessageBox
from pathlib import Path
from typing import Optional
from ..models.seating_plan import SeatingPlan

_last_dir: Path | None = None  # remembers last used folder

def _get_suggested_filename(seating_plan: SeatingPlan) -> str:
    """Generate a filename suggestion based on plan content."""
    if seating_plan:
        suggested_name = seating_plan.name.strip().replace(" ", "_").lower()
        return f"{suggested_name}.json"
    return "seating_plan.json"

def import_project_dialog(parent) -> Optional[SeatingPlan]:
    """Show a file dialog for importing a seating plan JSON file."""
    global _last_dir
    start_dir = str(_last_dir) if _last_dir else ""
    path, _ = QFileDialog.getOpenFileName(
        parent,
        "Import seating plan JSON",
        start_dir,
        "JSON Files (*.json; *.seatproj);;All Files (*)"
    )
    if path:
        try:
            sp = SeatingPlan()
            sp.import_project(path)
            _last_dir = Path(path).parent
            return sp
        except Exception as e:
            QMessageBox.warning(parent, "Import Failed", f"Could not load file:\n{e}")
    return None

def import_from_excel_dialog(parent) -> Optional[SeatingPlan]:
    """Show a file dialog for importing a seating plan from an Excel file."""
    global _last_dir
    start_dir = str(_last_dir) if _last_dir else ""
    path, _ = QFileDialog.getOpenFileName(
        parent,
        "Import seating plan from Excel",
        start_dir,
        "Excel Files (*.xlsx);;All Files (*)"
    )
    if path:
        try:
            # Ask for seating plan name
            from PyQt6.QtWidgets import QInputDialog
            default_name = Path(path).stem  # filename without extension
            plan_name, ok = QInputDialog.getText(
                parent,
                "Seating Plan Name",
                "Enter a name for this seating plan:",
                text=default_name
            )
            if not ok:
                return None
            
            plan_name = plan_name.strip() or default_name
            
            sp = SeatingPlan(plan_name)
            sp.import_from_excel(path)
            _last_dir = Path(path).parent
            return sp
        except Exception as e:
            QMessageBox.warning(parent, "Import Failed", f"Could not load file:\n{e}")
    return None

def import_from_avail_dialog(parent) -> Optional[SeatingPlan]:
    """Show a file dialog for importing a seating plan from an Avail XML file."""
    global _last_dir
    start_dir = str(_last_dir) if _last_dir else ""
    path, _ = QFileDialog.getOpenFileName(
        parent,
        "Import seating plan from Avail XML",
        start_dir,
        "XML Files (*.xml);;All Files (*)"
    )
    if path:
        try:
            # Ask for seating plan name
            from PyQt6.QtWidgets import QInputDialog
            default_name = Path(path).stem  # filename without extension
            plan_name, ok = QInputDialog.getText(
                parent,
                "Seating Plan Name",
                "Enter a name for this seating plan:",
                text=default_name
            )
            if not ok:
                return None
            
            plan_name = plan_name.strip() or default_name
            
            sp = SeatingPlan(plan_name)
            sp.import_from_avail(path)
            _last_dir = Path(path).parent
            return sp
        except Exception as e:
            QMessageBox.warning(parent, "Import Failed", f"Could not load file:\n{e}")
    return None

def export_project_dialog(parent, seating_plan: SeatingPlan) -> None:
    """Show a dialog to export the current seating plan as JSON."""
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
    try:
        seating_plan.export_project(path)
        _last_dir = Path(path).parent
    except Exception as e:
        QMessageBox.warning(parent, "Export Failed", f"Could not export file:\n{e}")

def export_to_excel_dialog(parent, seating_plan: SeatingPlan) -> None:
    """Show a dialog to export the current seating plan as an Excel file."""
    global _last_dir
    start_dir = str(_last_dir) if _last_dir else ""
    suggested_name = _get_suggested_filename(seating_plan).replace(".json", ".xlsx")
    suggested_name = 'manifest_' + suggested_name
    path, _ = QFileDialog.getSaveFileName(
        parent,
        "Export seating plan to Excel",
        str(Path(start_dir) / suggested_name),
        "Excel Files (*.xlsx);;All Files (*)"
    )
    if not path:
        return

    # ensure .xlsx extension
    if not path.lower().endswith(".xlsx"):
        path += ".xlsx"
    try:
        seating_plan.export_to_excel(path)
        _last_dir = Path(path).parent
    except Exception as e:
        QMessageBox.warning(parent, "Export Failed", f"Could not export file:\n{e}")



