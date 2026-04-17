"""Commands for seat-level operations."""

from typing import List

from ...domain.models.section import Section
from ...domain.exceptions import ValidationError
from .base import Command


class AddSeatCommand(Command):
    """Command to add a single seat to a section."""
    
    def __init__(self, section: Section, row: str, seat_number: str):
        """Initialize add seat command.
        
        Args:
            section: The Section to modify
            row: Row number/label
            seat_number: Seat number/label
        """
        super().__init__(f"Add seat {row}-{seat_number}")
        self.section = section
        self.row = row
        self.seat_number = seat_number
        self.seat_key = f"{row}-{seat_number}"
    
    def execute(self) -> None:
        """Add the seat."""
        if self.seat_key in self.section.seats:
            raise ValidationError(f"Seat {self.seat_key} already exists")
        
        self.section.add_seat(self.row, self.seat_number)
        self._executed = True
    
    def undo(self) -> None:
        """Remove the seat."""
        self.section.delete_seat(self.row, self.seat_number)


class DeleteSeatCommand(Command):
    """Command to delete a single seat from a section."""
    
    def __init__(self, section: Section, row: str, seat_number: str):
        """Initialize delete seat command.
        
        Args:
            section: The Section to modify
            row: Row number/label
            seat_number: Seat number/label
        """
        super().__init__(f"Delete seat {row}-{seat_number}")
        self.section = section
        self.row = row
        self.seat_number = seat_number
        self.seat_key = f"{row}-{seat_number}"
    
    def execute(self) -> None:
        """Delete the seat."""
        if self.seat_key not in self.section.seats:
            raise ValidationError(f"Seat {self.seat_key} not found")
        
        self.section.delete_seat(self.row, self.seat_number)
        self._executed = True
    
    def undo(self) -> None:
        """Restore the seat."""
        self.section.add_seat(self.row, self.seat_number)


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
        self._executed = True
    
    def undo(self) -> None:
        """Restore all seats in the row."""
        for key, seat in self._saved_seats.items():
            self.section.seats[key] = seat


class AddSeatRangeCommand(Command):
    """Command to add a range of seats to a section."""
    
    def __init__(
        self,
        section: Section,
        row: str,
        start_seat: str,
        end_seat: str,
        seat_prefix: str = "",
        seat_suffix: str = "",
        parity: str = "all"
    ):
        """Initialize add seat range command.
        
        Args:
            section: The Section to modify
            row: Row number/label
            start_seat: First seat in range
            end_seat: Last seat in range
            seat_prefix: Optional prefix for seat labels
            seat_suffix: Optional suffix for seat labels
            parity: Filter ('all', 'even', 'odd')
        """
        super().__init__(
            f"Add seats {row}: {start_seat}-{end_seat} ({parity})"
        )
        self.section = section
        self.row = row
        self.start_seat = start_seat
        self.end_seat = end_seat
        self.seat_prefix = seat_prefix
        self.seat_suffix = seat_suffix
        self.parity = parity
        self._added_keys: List[str] = []
    
    def execute(self) -> None:
        """Add the seat range."""
        # Remember what exists before
        before = set(self.section.seats.keys())
        
        self.section.add_seat_range(
            self.row,
            self.start_seat,
            self.end_seat,
            self.seat_prefix,
            self.seat_suffix,
            self.parity
        )
        
        # Track what was added
        after = set(self.section.seats.keys())
        self._added_keys = list(after - before)
        self._executed = True
    
    def undo(self) -> None:
        """Remove the added seats."""
        for key in self._added_keys:
            if key in self.section.seats:
                del self.section.seats[key]


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
        
        self._executed = True
    
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
        self._executed = True
    
    def undo(self) -> None:
        """Remove the added seats."""
        for key in self._added_keys:
            if key in self.section.seats:
                del self.section.seats[key]


class RenumberRowsCommand(Command):
    """Command to renumber rows in a section."""
    
    def __init__(
        self,
        section: Section,
        old_rows: List[str],
        new_start_row: str,
        add_prefix: bool = False,
    ):
        """Initialize renumber rows command.
        
        Args:
            section: The Section to modify
            old_rows: List of old row numbers to renumber (in order)
            new_start_row: Starting row number for new numbering
            add_prefix: If True, add '#' prefix to all new row numbers
        """
        super().__init__(f"Renumber {len(old_rows)} rows starting from {new_start_row}")
        self.section = section
        self.old_rows = old_rows
        self.new_start_row = new_start_row
        self.add_prefix = add_prefix
        self._old_state: dict = {}  # Save row numbers before renumbering
    
    def execute(self) -> None:
        """Renumber the rows."""
        # Save old state for undo - map old_row -> new_row
        for old_row in self.old_rows:
            self._old_state[old_row] = old_row  # Will be overwritten in section
        
        # Perform renumbering via section's method
        self.section.renumber_rows(self.old_rows, self.new_start_row, self.add_prefix)
        self._executed = True
    
    def undo(self) -> None:
        """Restore the old row numbers."""
        # Get the new row numbers that were created
        new_rows = []
        try:
            # Try to generate what the new rows should be
            from ...infrastructure.utils.alphanum_handler import alphanum_range
            start = self.new_start_row
            if self.add_prefix:
                start = start.lstrip('#')
            new_rows = alphanum_range(start, str(int(start) + len(self.old_rows) - 1)) if start.isdigit() else None
            if not new_rows:
                new_rows = [f"#{i}" for i in range(len(self.old_rows))]
        except:
            # Fallback: assume sequential numbers
            new_rows = [f"{self.new_start_row}_{i}" for i in range(len(self.old_rows))]
        
        # Restore old row numbers by renumbering back
        if len(new_rows) == len(self.old_rows):
            self.section.renumber_rows(new_rows, self.old_rows[0], False)

