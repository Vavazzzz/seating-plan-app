import json
from openpyxl import Workbook
from typing import Dict, Any
from .section import Section

class SeatingPlan:
    """Represents an entire seating plan project with multiple sections."""

    def __init__(self, name: str = "Unnamed Plan") -> None:
        self.sections: Dict[str, Section] = {}
        self.name: str = name or "Unnamed Plan"

    # ---- Section Manipulation ----
    def add_section(self, name: str) -> None:
        if name not in self.sections:
            self.sections[name] = Section(name)

    def delete_section(self, name: str) -> None:
        self.sections.pop(name, None)

    def rename_section(self, old_name: str, new_name: str) -> None:
        if old_name in self.sections and new_name not in self.sections:
            section = self.sections.pop(old_name)
            section.rename(new_name)
            self.sections[new_name] = section

    def clone_section(self, name: str, new_name: str) -> None:
        if name in self.sections and new_name not in self.sections:
            cloned = self.sections[name].clone()
            cloned.name = new_name
            self.sections[new_name] = cloned

    # ---- Serialization ----
    def to_dict(self) -> dict:
        return {
            "seating_plan_name": self.name,
            "sections": [section.to_dict() for section in self.sections.values()]
        }

    def from_dict(self, data: dict) -> None:
        self.name = data.get("seating_plan_name", "Unnamed Plan")
        self.sections = {}
        for section_data in data.get("sections", []):
            section = Section.from_dict(section_data)
            self.sections[section.name] = section

    # ---- File I/O ----
    def export_project(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def import_project(self, file_path: str) -> None:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.from_dict(data)

    def export_to_excel(self, file_path: str) -> None:
        wb = Workbook()
        ws = wb.active
        ws.title = "Seating Plan"

        headers = ["section", "rows", "seats", "secnam", "capacity", "type"]
        ws.append(headers)

        # Iterate through sections and rows
        for section in self.sections.values():
            rows = {}
            for seat in section.seats.values():
                rows.setdefault(seat.row_number, []).append(str(seat.seat_number))

            for row_number, seat_list in rows.items():
                try:
                    seat_list_sorted = sorted(seat_list, key=lambda x: int(x) if x.isdigit() else x)
                except ValueError:
                    seat_list_sorted = sorted(seat_list)
                ws.append([
                    section.name,             # section
                    row_number,               # rows
                    ",".join(seat_list_sorted),  # seats
                    section.name,             # secnam
                    "",                       # capacity (blank)
                    0                         # type (always 0)
                ])
        wb.save(file_path)