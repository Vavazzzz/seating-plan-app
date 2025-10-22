class SeatingPlan:
    def __init__(self):
        self.sections = {}

    def add_section(self, name):
        if name not in self.sections:
            self.sections[name] = Section(name)

    def delete_section(self, name):
        if name in self.sections:
            del self.sections[name]

    def rename_section(self, old_name, new_name):
        if old_name in self.sections and new_name not in self.sections:
            self.sections[new_name] = self.sections.pop(old_name)

    def export_to_json(self):
        return {name: section.to_dict() for name, section in self.sections.items()}

    def import_from_json(self, data):
        for name, section_data in data.items():
            section = Section(name)
            section.from_dict(section_data)
            self.sections[name] = section


class Section:
    def __init__(self, name):
        self.name = name
        self.seats = {}

    def add_seat(self, row, seat):
        if row not in self.seats:
            self.seats[row] = []
        if seat not in self.seats[row]:
            self.seats[row].append(seat)

    def delete_seat(self, row, seat):
        if row in self.seats and seat in self.seats[row]:
            self.seats[row].remove(seat)
            if not self.seats[row]:
                del self.seats[row]

    def delete_row(self, row):
        if row in self.seats:
            del self.seats[row]

    def to_dict(self):
        return self.seats

    def from_dict(self, data):
        self.seats = data


class Seat:
    def __init__(self, row_number, seat_number):
        self.row_number = row_number
        self.seat_number = seat_number

    def __repr__(self):
        return f"Seat({self.row_number}, {self.seat_number})"