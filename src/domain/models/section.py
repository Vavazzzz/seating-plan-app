from typing import Dict, Union, List
from collections import defaultdict
import copy
from .seat import Seat
from infrastructure.utils.alphanum_handler import alphanum_range, to_index, from_index

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

    def add_seat_range(
        self, 
        row: str, 
        start_seat: Union[int, str], 
        end_seat: Union[int, str],
        seat_prefix: str = "",
        seat_suffix: str = "",
        parity: str = "all"
    ) -> None:
        """
        Add seats for a given 'row' between start_seat and end_seat inclusive.
        """
        s_start = str(start_seat)
        s_end = str(end_seat)

        seats = alphanum_range(s_start, s_end)
        if not seats:
            try:
                a = int(s_start)
                b = int(s_end)
                if a > b: a, b = b, a
                seats = [str(i) for i in range(a, b + 1)]
            except Exception:
                return

        for s in seats:
            if parity != "all" and s.isdigit():
                val = int(s)
                if (parity == "even" and val % 2 != 0) or (parity == "odd" and val % 2 == 0):
                    continue
            elif parity != "all" and not s.isdigit():
                continue
                
            self.add_seat(row, f"{seat_prefix}{s}{seat_suffix}")

    def add_rows_bulk(
        self, 
        rows: list[str], 
        start_seat: str, 
        end_seat: str, 
        seat_prefix: str = "", 
        seat_suffix: str = "", 
        parity: str = "all", 
        continuous: bool = False
    ) -> None:
        """Handles complex bulk seat addition logic for multiple rows."""
        if continuous:
            try:
                s0, s1 = int(start_seat), int(end_seat)
                current_val = min(s0, s1)
                seats_per_row = abs(s1 - s0) + 1
                
                for row in rows:
                    added_in_row = 0
                    while added_in_row < seats_per_row:
                        seat_label = str(current_val)
                        is_even = current_val % 2 == 0
                        if parity == "all" or (parity == "even" and is_even) or (parity == "odd" and not is_even):
                            self.add_seat(row, f"{seat_prefix}{seat_label}{seat_suffix}")
                        added_in_row += 1
                        current_val += 1
                return
            except ValueError:
                pass # Fall back to standard range if not numeric

        for row in rows:
            self.add_seat_range(row, start_seat, end_seat, seat_prefix, seat_suffix, parity)

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

    def renumber_rows(self, old_rows_ordered: list[str], new_start_row: str, add_prefix: bool = False):
        """
        Renumber multiple rows sequentially starting from new_start_row.
        
        Args:
            old_rows_ordered: List of row numbers to renumber (in order)
            new_start_row:  Starting row number (can be numeric or alphanumeric)
            add_prefix: If True, add '#' prefix to all new row numbers
        """
        if not old_rows_ordered: 
            return
        
        # Determine if we're working with digits or letters
        is_digit = new_start_row.isdigit()
        start_idx = to_index(new_start_row)
        
        # Generate new row numbers
        new_rows = [
            from_index(start_idx + i, is_digit) 
            for i in range(len(old_rows_ordered))
        ]
        
        # Add prefix if requested
        if add_prefix:
            new_rows = [f"#{row}" for row in new_rows]
        
        # Build mapping of old -> new rows
        row_mapping = dict(zip(old_rows_ordered, new_rows))
        
        # Create a list of (old_key, new_key) pairs
        changes = []
        for old_key in list(self.seats.keys()):
            seat = self.seats[old_key]
            old_row = seat.row_number
            if old_row in row_mapping:
                new_row = row_mapping[old_row]
                _, seat_number = old_key. split('-', 1)
                new_key = f"{new_row}-{seat_number}"
                changes.append((old_key, new_key, new_row))
        
        # Apply changes
        for old_key, new_key, new_row in changes:
            seat = self.seats[old_key]
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
        """Serialize section to hierarchical JSON structure."""
        # Group seats by row efficiently using defaultdict
        rows_dict = defaultdict(list)
        for seat in self.seats.values():
            rows_dict[seat.row_number].append({"seat_number": seat.seat_number})
        
        rows = [
            {
                "row_number": row_number,
                "seats": seats
            }
            for row_number, seats in rows_dict.items()
        ]
        
        return {
            "name": self.name,
            "is_ga": self.is_ga,
            "rows": rows
        }

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