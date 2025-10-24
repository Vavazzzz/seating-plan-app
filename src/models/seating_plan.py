# src/models/seating_plan.py
from .section import Section
import json
from typing import Dict, List

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
