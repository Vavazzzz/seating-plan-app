"""Service for seat-level operations."""

from typing import List, Tuple
from .base import BaseService
from ..result import Result, ValidationErrors
from ..commands.seat_commands import (
    DeleteRowCommand,
    DeleteSeatsCommand,
    AddRowsCommand,
    RenumberRowsCommand,
    MoveSeatsCommand,
)


class SeatService(BaseService):
    """High-level service for seat operations.

    Provides validated, undo-enabled operations on seats within sections.
    """

    def delete_row(self, section_name: str, row: str) -> Result[None, ValidationErrors]:
        """Delete all seats in a row.

        Args:
            section_name: Name of section
            row: Row identifier

        Returns:
            Result.success() on success, validation errors on failure
        """
        self.clear_validation_errors()

        # Validation
        if not section_name or not section_name.strip():
            self.validate(False, "Section name cannot be empty")
        elif section_name not in self.seating_plan.sections:
            self.validate(False, f"Section '{section_name}' not found")
        elif not row or not row.strip():
            self.validate(False, "Row cannot be empty")

        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())

        try:
            section = self.seating_plan.sections[section_name]
            cmd = DeleteRowCommand(section, row)
            self.command_handler.execute(cmd)
            return Result.success(None)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to delete row: {str(e)}")
            return Result.failure(errors)

    def delete_seats(
        self,
        section_name: str,
        seats_to_delete: List[Tuple[str, str]],
    ) -> Result[None, ValidationErrors]:
        """Delete multiple specific seats from a section.

        Args:
            section_name: Name of section
            seats_to_delete: List of (row, seat) tuples to delete

        Returns:
            Result.success() on success, validation errors on failure
        """
        self.clear_validation_errors()

        # Validation
        if not section_name or not section_name.strip():
            self.validate(False, "Section name cannot be empty")
        elif section_name not in self.seating_plan.sections:
            self.validate(False, f"Section '{section_name}' not found")
        elif not seats_to_delete:
            self.validate(False, "At least one seat must be specified")

        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())

        try:
            section = self.seating_plan.sections[section_name]
            # Convert tuples to seat keys
            seat_keys = [f"{row}-{seat}" for row, seat in seats_to_delete]
            cmd = DeleteSeatsCommand(section, seat_keys)
            self.command_handler.execute(cmd)
            return Result.success(None)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to delete seats: {str(e)}")
            return Result.failure(errors)

    def add_rows_bulk(
        self,
        section_name: str,
        rows: List[str],
        start_seat: str,
        end_seat: str,
        seat_prefix: str = "",
        seat_suffix: str = "",
        parity: str = "all",
        continuous: bool = False,
    ) -> Result[int, ValidationErrors]:
        """Add multiple rows with seat ranges.

        Args:
            section_name: Name of section
            rows: List of row numbers/labels to add
            start_seat: Starting seat for each row
            end_seat: Ending seat for each row
            seat_prefix: Optional prefix for seat labels
            seat_suffix: Optional suffix for seat labels
            parity: Filter ('all', 'even', 'odd')
            continuous: If True, incrementally advance seats across rows

        Returns:
            Result with total seat count on success, validation errors on failure
        """
        self.clear_validation_errors()

        # Validation
        if not section_name or not section_name.strip():
            self.validate(False, "Section name cannot be empty")
        elif section_name not in self.seating_plan.sections:
            self.validate(False, f"Section '{section_name}' not found")
        elif not rows:
            self.validate(False, "At least one row must be specified")
        elif not start_seat or not start_seat.strip():
            self.validate(False, "Start seat cannot be empty")
        elif not end_seat or not end_seat.strip():
            self.validate(False, "End seat cannot be empty")

        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())

        try:
            section = self.seating_plan.sections[section_name]
            cmd = AddRowsCommand(
                section,
                rows,
                start_seat,
                end_seat,
                seat_prefix=seat_prefix,
                seat_suffix=seat_suffix,
                parity=parity,
                continuous=continuous,
            )
            self.command_handler.execute(cmd)

            # Return total count of seats added
            total_seats = len(section.seats)
            return Result.success(total_seats)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to add rows: {str(e)}")
            return Result.failure(errors)

    def move_seats(
        self,
        source_name: str,
        target_name: str,
        seats: list[tuple[str, str]],
    ) -> Result[int, ValidationErrors]:
        """Move seats from one section to another as a single undoable operation.

        Seats that already exist in the target are skipped (no overwrite).

        Args:
            source_name: Section to move seats from
            target_name: Section to move seats into
            seats: List of (row, seat) tuples to move

        Returns:
            Result with count of seats actually moved on success
        """
        self.clear_validation_errors()

        if not source_name or not source_name.strip():
            self.validate(False, "Source section name cannot be empty")
        elif source_name not in self.seating_plan.sections:
            self.validate(False, f"Source section '{source_name}' not found")

        if not target_name or not target_name.strip():
            self.validate(False, "Target section name cannot be empty")
        elif target_name not in self.seating_plan.sections:
            self.validate(False, f"Target section '{target_name}' not found")
        elif source_name == target_name:
            self.validate(False, "Source and target sections must be different")

        if not seats:
            self.validate(False, "At least one seat must be specified")

        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())

        try:
            cmd = MoveSeatsCommand(self.seating_plan, source_name, target_name, seats)
            self.command_handler.execute(cmd)
            return Result.success(len(cmd._moved))
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to move seats: {str(e)}")
            return Result.failure(errors)

    def renumber_rows(
        self,
        section_name: str,
        old_rows: List[str],
        new_start_row: str,
        add_prefix: bool = False,
    ) -> Result[None, ValidationErrors]:
        """Renumber rows in a section.

        Args:
            section_name: Name of section
            old_rows: List of old row numbers to renumber (in order)
            new_start_row: Starting row number for new numbering
            add_prefix: If True, add '#' prefix to all new row numbers

        Returns:
            Result.success() on success, validation errors on failure
        """
        self.clear_validation_errors()

        # Validation
        if not section_name or not section_name.strip():
            self.validate(False, "Section name cannot be empty")
        elif section_name not in self.seating_plan.sections:
            self.validate(False, f"Section '{section_name}' not found")
        elif not old_rows:
            self.validate(False, "At least one row must be specified")
        elif not new_start_row or not new_start_row.strip():
            self.validate(False, "Starting row number cannot be empty")

        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())

        try:
            section = self.seating_plan.sections[section_name]
            cmd = RenumberRowsCommand(section, old_rows, new_start_row, add_prefix)
            self.command_handler.execute(cmd)
            return Result.success(None)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to renumber rows: {str(e)}")
            return Result.failure(errors)
