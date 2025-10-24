# src/utils/json_io.py
from PyQt6.QtWidgets import QFileDialog
from typing import Optional
from ..models.seating_plan import SeatingPlan

def import_json_dialog(parent) -> Optional[SeatingPlan]:
    path, _ = QFileDialog.getOpenFileName(parent, "Import seating plan JSON", "", "JSON Files (*.json);;All Files (*)")
    if path:
        sp = SeatingPlan()
        sp.import_from_json(path)
        return sp
    return None

def export_json_dialog(parent, seating_plan: SeatingPlan):
    path, _ = QFileDialog.getSaveFileName(parent, "Export seating plan JSON", "", "JSON Files (*.json);;All Files (*)")
    if path:
        seating_plan.export_to_json(path)
