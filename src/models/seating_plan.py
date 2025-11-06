# src/models/seating_plan.py
import json
from openpyxl import Workbook
from typing import Dict
from .section import Section

class SeatingPlan:
    def __init__(self):
        self.sections: Dict[str, Section] = {}

    def add_section(self, name):
        if name not in self.sections:
            self.sections[name] = Section(name)

    def delete_section(self, name):
        if name in self.sections:
            del self.sections[name]

    def rename_section(self, old_name: str, new_name: str):
        if old_name in self.sections and new_name not in self.sections:
            section = self.sections[old_name]
            section.rename(new_name)
            self.sections[new_name] = section
            del self.sections[old_name]

    def clone_section(self, name, new_name):
        if name in self.sections and new_name not in self.sections:
            cloned = self.sections[name].clone()
            cloned.name = new_name
            self.sections[new_name] = cloned

    # ---------- JSON (new hierarchical format) ----------
    def to_dict(self):
        return {
            "sections": [section.to_dict() for section in self.sections.values()]
        }

    def from_dict(self, data):
        self.sections = {}
        for section_data in data.get("sections", []):
            section = Section.from_dict(section_data)
            self.sections[section.name] = section

    def export_to_json(self, file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def import_from_json(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.from_dict(data)

    def export_to_excel(self, file_path):
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Seating Plan"

        headers = ["section", "row", "seat_number", "seat_name", "capacity", "type"]
        ws.append(headers)

        # Iterate through sections and rows
        for section in self.sections.values():
            rows = {}
            for seat in section.seats.values():
                rows.setdefault(seat.row_number, []).append(str(seat.seat_number))

            for row_number, seat_list in rows.items():
                seat_list_sorted = sorted(seat_list, key=lambda x: int(x) if x.isdigit() else x)
                ws.append([
                    section.name,             # section
                    row_number,               # rows
                    ",".join(seat_list_sorted),# seats
                    section.name,             # secnam
                    "",                       # capacity (blank)
                    1                         # type (always 1)
                ])


        wb.save(file_path)
