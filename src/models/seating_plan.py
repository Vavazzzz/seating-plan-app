import json
import re
from openpyxl import Workbook
from typing import Dict, Any, List
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

    def clone_section_many(self, name: str, count: int) -> List[str]:
        """
        Clone the given section 'count' times, returning a list of created section names.

        Naming strategy:
        - If the source name ends with a numeric suffix (e.g. "Section 1"), the clones will
          continue numbering from that suffix +1 (e.g. 2,3,...).
        - If the source name has no numeric suffix, clones will be created as "Name 2",
          "Name 3", ... (starting numbering at 2).
        - If a generated candidate name already exists, it is skipped by advancing the number
          until an unused name is found. Exactly 'count' new sections will be created.
        """
        created: List[str] = []
        if name not in self.sections or count <= 0:
            return created

        # Try to find a prefix and a start number. Example matches:
        #  - "I Ordine Palco 1" -> prefix="I Ordine Palco", start=1
        #  - "Balcony" -> prefix="Balcony", start=None -> we'll treat start as 1
        m = re.match(r"^(.*\S)(?:\s+(\d+))?$", name)
        if not m:
            prefix = name
            start_num = 1
        else:
            prefix = m.group(1) if m.group(1) else name
            start_num = int(m.group(2)) if m.group(2) else 1

        current = start_num + 1
        for _ in range(count):
            # find next unused candidate name
            candidate = f"{prefix} {current}"
            while candidate in self.sections:
                current += 1
                candidate = f"{prefix} {current}"
            # clone and register
            cloned = self.sections[name].clone()
            cloned.name = candidate
            self.sections[candidate] = cloned
            created.append(candidate)
            current += 1

        return created

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

    def import_from_excel(self, file_path: str) -> None:
        from openpyxl import load_workbook

        wb = load_workbook(filename=file_path, read_only=True)
        ws = wb.active
        
        headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
        header_indices = {header: idx for idx, header in enumerate(headers) if header is not None}

        required_headers = {"section", "rows", "seats"}
        if not required_headers.issubset(header_indices.keys()):
            raise ValueError(f"Excel file must contain headers: {', '.join(required_headers)}")

        for row in ws.iter_rows(min_row=2):
            section_name = row[header_indices["section"]].value
            row_identifier = row[header_indices["rows"]].value
            seats_str = row[header_indices["seats"]].value

            if section_name is None or row_identifier is None or seats_str is None:
                continue

            if section_name not in self.sections:
                self.add_section(section_name)

            seat_labels = [s.strip() for s in seats_str.split(",") if s.strip()]
            for seat_label in seat_labels:
                self.sections[section_name].add_seat(row_identifier, seat_label)

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