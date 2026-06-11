"""Commands for seat-level operations."""

from typing import List

from domain.models.section import Section
from domain.models.seating_plan import SeatingPlan
from domain.exceptions import ValidationError
from .base import Command


class DeleteRowCommand(Command):
    """Command to delete all seats in a row."""

    def __init__(self, section: Section, row: str):
        """Initialize delete row command.

        Args:
            section: The Section to modify
            row: Row number/label to delete
        """
        super().__init__(f"Delete row {row}")
        self.section = section
        self.row = row
        self._saved_seats: dict = {}

    def execute(self) -> None:
        """Delete all seats in the row."""
        # Find and save all seats in this row
        keys_to_delete = [
            key for key in self.section.seats
            if key.startswith(f"{self.row}-")
        ]

        if not keys_to_delete:
            raise ValidationError(f"No seats found in row {self.row}")

        for key in keys_to_delete:
            seat = self.section.seats[key]
            self._saved_seats[key] = seat

        self.section.delete_row(self.row)

    def undo(self) -> None:
        """Restore all seats in the row."""
        for key, seat in self._saved_seats.items():
            self.section.seats[key] = seat


class DeleteSeatsCommand(Command):
    """Command to delete multiple seats."""

    def __init__(self, section: Section, seat_keys: List[str]):
        """Initialize delete multiple seats command.

        Args:
            section: The Section to modify
            seat_keys: List of seat keys (format "row-seat")
        """
        super().__init__(f"Delete {len(seat_keys)} seats")
        self.section = section
        self.seat_keys = seat_keys
        self._saved_seats: dict = {}

    def execute(self) -> None:
        """Delete the seats."""
        for key in self.seat_keys:
            if key not in self.section.seats:
                raise ValidationError(f"Seat {key} not found")

            # Save for undo
            self._saved_seats[key] = self.section.seats[key]

        # Delete all
        for key in self.seat_keys:
            del self.section.seats[key]

    def undo(self) -> None:
        """Restore the deleted seats."""
        for key, seat in self._saved_seats.items():
            self.section.seats[key] = seat


class AddRowsCommand(Command):
    """Command to add multiple rows with seat ranges (supports continuous mode)."""

    def __init__(
        self,
        section: Section,
        rows: List[str],
        start_seat: str,
        end_seat: str,
        seat_prefix: str = "",
        seat_suffix: str = "",
        parity: str = "all",
        continuous: bool = False,
    ):
        """Initialize add rows command.

        Args:
            section: The Section to modify
            rows: List of row numbers/labels to add
            start_seat: Starting seat for each row
            end_seat: Ending seat for each row
            seat_prefix: Optional prefix for seat labels
            seat_suffix: Optional suffix for seat labels
            parity: Filter ('all', 'even', 'odd')
            continuous: If True, incrementally advance seats across rows
        """
        super().__init__(f"Add {len(rows)} rows with seats {start_seat}-{end_seat}")
        self.section = section
        self.rows = rows
        self.start_seat = start_seat
        self.end_seat = end_seat
        self.seat_prefix = seat_prefix
        self.seat_suffix = seat_suffix
        self.parity = parity
        self.continuous = continuous
        self._added_keys: List[str] = []

    def execute(self) -> None:
        """Add rows with seat ranges using bulk logic."""
        before = set(self.section.seats.keys())

        # Use the section's add_rows_bulk method which handles continuous mode
        self.section.add_rows_bulk(
            rows=self.rows,
            start_seat=self.start_seat,
            end_seat=self.end_seat,
            seat_prefix=self.seat_prefix,
            seat_suffix=self.seat_suffix,
            parity=self.parity,
            continuous=self.continuous,
        )

        # Track what was added for undo
        after = set(self.section.seats.keys())
        self._added_keys = list(after - before)

    def undo(self) -> None:
        """Remove the added seats."""
        for key in self._added_keys:
            if key in self.section.seats:
                del self.section.seats[key]


class MoveSeatsCommand(Command):
    """Command to move seats from one section to another atomically."""

    def __init__(
        self,
        seating_plan: SeatingPlan,
        source_name: str,
        target_name: str,
        seats: list[tuple[str, str]],
    ):
        super().__init__(f"Move {len(seats)} seats from '{source_name}' to '{target_name}'")
        self.seating_plan = seating_plan
        self.source_name = source_name
        self.target_name = target_name
        self.seats = seats
        self._moved: list[tuple[str, str]] = []
        self._skipped: list[tuple[str, str]] = []

    def execute(self) -> None:
        source = self.seating_plan.sections[self.source_name]
        target = self.seating_plan.sections[self.target_name]
        self._moved = []
        self._skipped = []
        for row, seat in self.seats:
            key = f"{row}-{seat}"
            if key not in source.seats:
                continue
            if key in target.seats:
                self._skipped.append((row, seat))
                continue
            target.seats[key] = source.seats.pop(key)
            self._moved.append((row, seat))

    def undo(self) -> None:
        source = self.seating_plan.sections[self.source_name]
        target = self.seating_plan.sections[self.target_name]
        for row, seat in self._moved:
            key = f"{row}-{seat}"
            if key in target.seats:
                source.seats[key] = target.seats.pop(key)


class RenumberRowsCommand(Command):
    """Command to renumber rows in a section."""

    def __init__(
        self,
        section: Section,
        old_rows: List[str],
        new_start_row: str,
        add_prefix: bool = False,
    ):
        super().__init__(f"Renumber {len(old_rows)} rows starting from {new_start_row}")
        self.section = section
        self.old_rows = old_rows
        self.new_start_row = new_start_row
        self.add_prefix = add_prefix
        self._row_mapping: dict[str, str] = {}  # old_row -> new_row, captured at execute time

    def execute(self) -> None:
        self._row_mapping = self.section.renumber_rows(self.old_rows, self.new_start_row, self.add_prefix)

    def undo(self) -> None:
        reverse: dict[str, str] = {new: old for old, new in self._row_mapping.items()}
        changes = []
        for new_key in list(self.section.seats.keys()):
            seat = self.section.seats[new_key]
            if seat.row_number in reverse:
                old_row = reverse[seat.row_number]
                _, seat_number = new_key.split('-', 1)
                old_key = f"{old_row}-{seat_number}"
                changes.append((new_key, old_key, old_row))
        for new_key, old_key, old_row in changes:
            seat = self.section.seats[new_key]
            seat.row_number = old_row
            self.section.seats[old_key] = seat
            del self.section.seats[new_key]
