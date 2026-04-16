import json
import re
from typing import Dict, List
from .section import Section
from ..exceptions import MergeConflictError

class SeatingPlan:
    """Represents an entire seating plan project with multiple sections."""

    def __init__(self, name: str = "Unnamed Plan") -> None:
        self.sections: Dict[str, Section] = {}
        self.name: str = name or "Unnamed Plan"

    # ---- Section Manipulation ----
    def add_section(self, name: str, is_ga: bool = False) -> None:
        if name not in self.sections:
            self.sections[name] = Section(name, is_ga=is_ga)
            self.sections[name].is_ga = is_ga

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

    def merge_sections(self, source_section_names: List[str], new_section_name: str) -> None:
        """Create a new section containing all seats from the listed source sections.

        Conflicts (same row+seat present in more than one source) will abort the
        operation and raise MergeConflictError. The source sections are left
        unchanged.

        Args:
            source_section_names: list of existing section names to merge (>=2)
            new_section_name: name for the newly created section (must not exist)
        """
        # Validate input
        if not source_section_names or len(source_section_names) < 2:
            raise ValueError("Provide at least two source sections to merge")
        if new_section_name in self.sections:
            raise ValueError(f"Target section '{new_section_name}' already exists")

        # Collect source Section objects and validate existence
        sources: List[Section] = []
        for sname in source_section_names:
            if sname not in self.sections:
                raise KeyError(f"Source section '{sname}' does not exist")
            sources.append(self.sections[sname])

        # Build staging map and detect conflicts: seat_key -> list of source names
        seat_origins: Dict[str, List[str]] = {}
        for sec in sources:
            for key in sec.seats.keys():
                seat_origins.setdefault(key, []).append(sec.name)

        # Any seat key that appears more than once is a conflict
        conflicts = {k: v for k, v in seat_origins.items() if len(v) > 1}
        if conflicts:
            # Format a helpful message listing conflicting seat keys and origins
            msgs = [f"{k}: {','.join(v)}" for k, v in conflicts.items()]
            raise MergeConflictError("Conflicting seats detected: " + "; ".join(msgs))

        # No conflicts: create the new section and copy seats
        new_is_ga = all(sec.is_ga for sec in sources)
        new_section = Section(new_section_name, is_ga=new_is_ga)
        for sec in sources:
            for seat in sec.seats.values():
                new_section.add_seat(seat.row_number, seat.seat_number)

        # Register new section
        self.sections[new_section_name] = new_section

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