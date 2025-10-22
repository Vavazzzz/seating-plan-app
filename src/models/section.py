from typing import List, Dict
from .seat import Seat

class Section:
    def __init__(self, name: str):
        self.name = name
        self.seats: Dict[str, Seat] = {}

    def add_seat(self, row: str, seat_number: str):
        seat_key = f"{row}-{seat_number}"
        if seat_key not in self.seats:
            self.seats[seat_key] = Seat(row, seat_number)

    def add_seat_range(self, row: str, start_seat: int, end_seat: int):
        for seat_number in range(start_seat, end_seat + 1):
            self.add_seat(row, str(seat_number))

    def delete_seat(self, row: str, seat_number: str):
        seat_key = f"{row}-{seat_number}"
        if seat_key in self.seats:
            del self.seats[seat_key]

    def delete_row(self, row: str):
        keys_to_delete = [key for key in self.seats if key.startswith(f"{row}-")]
        for key in keys_to_delete:
            del self.seats[key]

    def rename(self, new_name: str):
        self.name = new_name

    def change_seat_number(self, row: str, old_seat_number: str, new_seat_number: str):
        old_key = f"{row}-{old_seat_number}"
        if old_key in self.seats:
            seat = self.seats[old_key]
            self.delete_seat(row, old_seat_number)
            self.add_seat(row, new_seat_number)

    def to_dict(self):
        return {
            "name": self.name,
            "seats": {key: seat.to_dict() for key, seat in self.seats.items()}
        }

    @classmethod
    def from_dict(cls, data):
        section = cls(data['name'])
        for seat_key, seat_data in data['seats'].items():
            section.seats[seat_key] = Seat.from_dict(seat_data)
        return section