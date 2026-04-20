"""Service for seat-level operations."""

from typing import List, Optional, Tuple
from .base import BaseService
from ..result import Result, ValidationErrors
from ..commands.seat_commands import (
    AddSeatCommand,
    DeleteSeatCommand,
    DeleteRowCommand,
    AddSeatRangeCommand,
    DeleteSeatsCommand,
    AddRowsCommand,
    RenumberRowsCommand,
)
from domain.models.section import Section


class SeatService(BaseService):
    """High-level service for seat operations.
    
    Provides validated, undo-enabled operations on seats within sections.
    """
    
    def add_seat(
        self,
        section_name: str,
        row: str,
        seat: str,
    ) -> Result[Tuple[str, str], ValidationErrors]:
        """Add a single seat to a section.
        
        Args:
            section_name: Name of section to add seat to
            row: Row identifier
            seat: Seat identifier
            
        Returns:
            Result with (row, seat) tuple on success, validation errors on failure
        """
        self.clear_validation_errors()
        
        # Validation
        if not section_name or not section_name.strip():
            self.validate(False, "Section name cannot be empty")
        elif section_name not in self.seating_plan.sections:
            self.validate(False, f"Section '{section_name}' not found")
        elif not row or not row.strip():
            self.validate(False, "Row cannot be empty")
        elif not seat or not seat.strip():
            self.validate(False, "Seat cannot be empty")
        
        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())
        
        try:
            section = self.seating_plan.sections[section_name]
            cmd = AddSeatCommand(section, row, seat)
            self.command_handler.execute(cmd)
            return Result.success((row, seat))
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to add seat: {str(e)}")
            return Result.failure(errors)
    
    def delete_seat(
        self,
        section_name: str,
        row: str,
        seat: str,
    ) -> Result[None, ValidationErrors]:
        """Delete a single seat from a section.
        
        Args:
            section_name: Name of section
            row: Row identifier
            seat: Seat identifier
            
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
        elif not seat or not seat.strip():
            self.validate(False, "Seat cannot be empty")
        
        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())
        
        try:
            section = self.seating_plan.sections[section_name]
            cmd = DeleteSeatCommand(section, row, seat)
            self.command_handler.execute(cmd)
            return Result.success(None)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to delete seat: {str(e)}")
            return Result.failure(errors)
    
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
    
    def add_seat_range(
        self,
        section_name: str,
        row: str,
        start_seat: str,
        end_seat: str,
    ) -> Result[int, ValidationErrors]:
        """Add multiple seats in a range within a row.
        
        Args:
            section_name: Name of section
            row: Row identifier
            start_seat: Starting seat identifier
            end_seat: Ending seat identifier
            
        Returns:
            Result with count of seats added on success, validation errors on failure
        """
        self.clear_validation_errors()
        
        # Validation
        if not section_name or not section_name.strip():
            self.validate(False, "Section name cannot be empty")
        elif section_name not in self.seating_plan.sections:
            self.validate(False, f"Section '{section_name}' not found")
        elif not row or not row.strip():
            self.validate(False, "Row cannot be empty")
        elif not start_seat or not start_seat.strip():
            self.validate(False, "Start seat cannot be empty")
        elif not end_seat or not end_seat.strip():
            self.validate(False, "End seat cannot be empty")
        
        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())
        
        try:
            section = self.seating_plan.sections[section_name]
            cmd = AddSeatRangeCommand(section, row, start_seat, end_seat)
            self.command_handler.execute(cmd)
            
            # Return count of seats added in the row
            seats_in_row = len([s for s in section.seats.values() if s.row_number == row])
            return Result.success(seats_in_row)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to add seat range: {str(e)}")
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
    
    def get_section_seats(self, section_name: str) -> Result[List[Tuple[str, str]], ValidationErrors]:
        """Get all seats in a section as (row, seat) tuples.
        
        Args:
            section_name: Name of section
            
        Returns:
            Result with list of (row, seat) tuples, validation errors if section not found
        """
        self.clear_validation_errors()
        
        if section_name not in self.seating_plan.sections:
            self.validate(False, f"Section '{section_name}' not found")
            return Result.failure(self.get_validation_errors())
        
        try:
            section = self.seating_plan.sections[section_name]
            seats = [(s.row_number, s.seat_number) for s in section.seats.values()]
            return Result.success(seats)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to get seats: {str(e)}")
            return Result.failure(errors)
    
    def get_section_rows(self, section_name: str) -> Result[List[str], ValidationErrors]:
        """Get all rows in a section, sorted.
        
        Args:
            section_name: Name of section
            
        Returns:
            Result with sorted list of row identifiers
        """
        self.clear_validation_errors()
        
        if section_name not in self.seating_plan.sections:
            self.validate(False, f"Section '{section_name}' not found")
            return Result.failure(self.get_validation_errors())
        
        try:
            section = self.seating_plan.sections[section_name]
            rows = sorted(set(s.row_number for s in section.seats.values()))
            return Result.success(rows)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to get rows: {str(e)}")
            return Result.failure(errors)
    
    def seat_exists(self, section_name: str, row: str, seat: str) -> bool:
        """Check if a specific seat exists.
        
        Args:
            section_name: Name of section
            row: Row identifier
            seat: Seat identifier
            
        Returns:
            True if seat exists, False otherwise
        """
        if section_name not in self.seating_plan.sections:
            return False
        
        section = self.seating_plan.sections[section_name]
        seat_key = f"{row}-{seat}"
        return seat_key in section.seats
    
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
