from typing import Dict, List, Any, Union
from .seat import Seat
import copy
from ..utils.alphanum_handler import alphanum_range

class Section:
    """Represents a section containing multiple seats."""

    def __init__(self, name: str, is_ga: bool = False) -> None:
        self.name: str = name
        # Seats keyed by "ROW-SEAT"
        self.seats: Dict[str, Seat] = {}
        self.is_ga: bool = is_ga

    # ---- Seat Manipulation ----
    def add_seat(self, row: str, seat_number: str) -> None:
        seat_key = f"{row}-{seat_number}"
        if seat_key not in self.seats:
            self.seats[seat_key] = Seat(row, seat_number)

    def add_seat_range(self, row: str, start_seat: Union[int, str], end_seat: Union[int, str]) -> None:
        """
        Add seats for a given 'row' between start_seat and end_seat inclusive.

        start_seat and end_seat may be ints (or strings of digits) or alphabetic labels
        (e.g. 'A'..'Z' or multi-letter like 'AA'). This uses alphanum_range() to generate
        the full list of labels and will add each seat label to the row.
        """
        # normalize to strings
        s_start = str(start_seat)
        s_end = str(end_seat)

        # build list using alphanumeric helper (handles numeric and alphabetic ranges)
        seats = alphanum_range(s_start, s_end)
        # If alphanum_range returns empty (invalid), attempt a best-effort fallback:
        if not seats:
            try:
                a = int(s_start)
                b = int(s_end)
                if a > b:
                    a, b = b, a
                seats = [str(i) for i in range(a, b + 1)]
            except Exception:
                # give up silently (no seats added) - caller/UI can warn
                return

        for s in seats:
            self.add_seat(row, str(s))

    def delete_seat(self, row: str, seat_number: str) -> None:
        seat_key = f"{row}-{seat_number}"
        self.seats.pop(seat_key, None)

    def delete_row(self, row: str) -> None:
        keys_to_delete = [key for key in self.seats if key.startswith(f"{row}-")]
        for key in keys_to_delete:
            del self.seats[key]

    # ---- Modification ----
    def rename(self, new_name: str) -> None:
        self.name = new_name

    def change_seat_number(self, row: str, old_seat_number: str, new_seat_number: str) -> None:
        old_key = f"{row}-{old_seat_number}"
        if old_key in self.seats:
            seat = self.seats.pop(old_key)
            seat.seat_number = new_seat_number
            new_key = f"{row}-{new_seat_number}"
            self.seats[new_key] = seat

    def change_row_number(self, old_row: str, new_row: str) -> None:
        keys_to_change = [k for k in self.seats.keys() if k.startswith(f"{old_row}-")]
        for old_key in keys_to_change:
            seat = self.seats[old_key]
            _, seat_number = old_key.split('-', 1)
            new_key = f"{new_row}-{seat_number}"
            seat.row_number = new_row
            self.seats[new_key] = seat
            del self.seats[old_key]

    def clone(self) -> 'Section':
        """Return a deep copy of this section with '_copy' appended to name."""
        new_section = Section(self.name + "_copy")
        for key, seat in self.seats.items():
            new_section.seats[key] = copy.deepcopy(seat)
        return new_section

    # ---- Serialization (JSON) ----
    def to_dict(self) -> dict:
        """Serialize section for hierarchical JSON structure."""
        rows: Dict[str, List[Seat]] = {}
        for seat in self.seats.values():
            rows.setdefault(seat.row_number, []).append(seat)
        rows_list = []
        for row_number, seats in rows.items():
            try:
                seats_sorted = sorted(seats, key=lambda s: int(s.seat_number))
            except ValueError:
                seats_sorted = sorted(seats, key=lambda s: s.seat_number)
            rows_list.append({
                "row_number": row_number,
                "seats": [{"seat_number": s.seat_number} for s in seats_sorted]
            })
        return {"name": self.name, "is_ga": self.is_ga, "rows": rows_list}

    @classmethod
    def from_dict(cls, data: dict) -> 'Section':
        """Deserialize section from hierarchical JSON structure."""
        section = cls(data["name"], is_ga=data.get("is_ga", False))
        for row_data in data.get("rows", []):
            row_number = row_data["row_number"]
            for seat_data in row_data.get("seats", []):
                seat_number = seat_data["seat_number"]
                section.add_seat(row_number, seat_number)
        return section