from .section import Section
import json

class SeatingPlan:
    def __init__(self):
        self.sections = {}

    def add_section(self, name):
        if name not in self.sections:
            self.sections[name] = Section(name)

    def delete_section(self, name):
        if name in self.sections:
            del self.sections[name]

    def clone_section(self, name, new_name):
        if name in self.sections and new_name not in self.sections:
            self.sections[new_name] = self.sections[name].clone()

    def to_dict(self):
        return {name: section.to_dict() for name, section in self.sections.items()}

    def from_dict(self, data):
        for name, section_data in data.items():
            section = Section(name)
            section.from_dict(section_data)
            self.sections[name] = section

    def export_to_json(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def import_from_json(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            self.from_dict(data)