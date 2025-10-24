# src/models/seating_plan.py
from .section import Section
import json
from typing import Dict

class SeatingPlan:
    def __init__(self):
        # map from section name -> Section
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
            # ensure keys keep consistent (keys are "row-seat" so fine)
            self.sections[new_name] = cloned

    def to_dict(self):
        return {name: section.to_dict() for name, section in self.sections.items()}

    def from_dict(self, data):
        self.sections = {}
        for name, section_data in data.items():
            section = Section.from_dict(section_data)
            # ensure name matches key
            section.name = name
            self.sections[name] = section

    def export_to_json(self, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def import_from_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.from_dict(data)
