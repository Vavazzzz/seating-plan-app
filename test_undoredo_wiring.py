#!/usr/bin/env python3
"""Test script to verify undo/redo functionality is wired correctly."""

from src.domain.models.seating_plan import SeatingPlan
from src.domain.models.section import Section
from src.application.services.seating_plan_service import SeatingPlanService
from src.application.services.seat_service import SeatService
from src.application.handlers.command_handler import CommandHandler


def test_delete_seats_undo_redo():
    """Test that seat deletion uses CommandHandler for undo/redo."""
    print("\n=== Test: Delete Seats Undo/Redo ===")
    
    # Setup
    seating_plan = SeatingPlan("Test Venue")
    seating_plan.add_section("Section A")
    section = seating_plan.sections["Section A"]
    
    command_handler = CommandHandler()
    seat_service = SeatService(seating_plan, command_handler)
    
    # Add some seats first
    section.add_seat("1", "A")
    section.add_seat("1", "B")
    section.add_seat("2", "A")
    print(f"Initial seats: {len(section.seats)}")  # Should be 3
    
    # Delete seats via service (should use CommandHandler)
    result = seat_service.delete_seats("Section A", [("1", "A"), ("1", "B")])
    print(f"Delete result: {result.is_success()}")
    print(f"After delete: {len(section.seats)}")  # Should be 1
    
    # Check undo is available
    can_undo = command_handler.can_undo()
    print(f"Can undo: {can_undo}")  # Should be True
    
    # Undo the delete
    if can_undo:
        command_handler.undo()
        print(f"After undo: {len(section.seats)}")  # Should be 3
    
    # Check redo is available
    can_redo = command_handler.can_redo()
    print(f"Can redo: {can_redo}")  # Should be True
    
    # Redo the delete
    if can_redo:
        command_handler.redo()
        print(f"After redo: {len(section.seats)}")  # Should be 1
    
    print("OK: Delete seats undo/redo working!")


def test_add_rows_bulk_undo_redo():
    """Test that bulk row addition uses CommandHandler for undo/redo."""
    print("\n=== Test: Add Rows Bulk Undo/Redo ===")
    
    # Setup
    seating_plan = SeatingPlan("Test Venue")
    seating_plan.add_section("Section B")
    section = seating_plan.sections["Section B"]
    
    command_handler = CommandHandler()
    seat_service = SeatService(seating_plan, command_handler)
    
    print(f"Initial seats: {len(section.seats)}")  # Should be 0
    
    # Add rows via service (should use CommandHandler)
    result = seat_service.add_rows_bulk(
        "Section B",
        rows=["A", "B", "C"],
        start_seat="1",
        end_seat="3",
        parity="all",
        continuous=False
    )
    print(f"Add result: {result.is_success()}")
    print(f"After add: {len(section.seats)}")  # Should be 9 (3 rows x 3 seats)
    
    # Check undo is available
    can_undo = command_handler.can_undo()
    print(f"Can undo: {can_undo}")  # Should be True
    
    # Undo the add
    if can_undo:
        command_handler.undo()
        print(f"After undo: {len(section.seats)}")  # Should be 0
    
    # Check redo is available
    can_redo = command_handler.can_redo()
    print(f"Can redo: {can_redo}")  # Should be True
    
    # Redo the add
    if can_redo:
        command_handler.redo()
        print(f"After redo: {len(section.seats)}")  # Should be 9
    
    print("OK: Add rows bulk undo/redo working!")


def test_delete_rows_undo_redo():
    """Test that row deletion uses CommandHandler for undo/redo."""
    print("\n=== Test: Delete Rows Undo/Redo ===")
    
    # Setup
    seating_plan = SeatingPlan("Test Venue")
    seating_plan.add_section("Section C")
    section = seating_plan.sections["Section C"]
    
    command_handler = CommandHandler()
    seat_service = SeatService(seating_plan, command_handler)
    
    # Add some seats first
    section.add_seat("1", "A")
    section.add_seat("1", "B")
    section.add_seat("2", "A")
    section.add_seat("2", "B")
    print(f"Initial seats: {len(section.seats)}")  # Should be 4
    
    # Delete row via service (should use CommandHandler)
    result = seat_service.delete_row("Section C", "1")
    print(f"Delete result: {result.is_success()}")
    print(f"After delete: {len(section.seats)}")  # Should be 2
    
    # Check undo is available
    can_undo = command_handler.can_undo()
    print(f"Can undo: {can_undo}")  # Should be True
    
    # Undo the delete
    if can_undo:
        command_handler.undo()
        print(f"After undo: {len(section.seats)}")  # Should be 4
    
    # Check redo is available
    can_redo = command_handler.can_redo()
    print(f"Can redo: {can_redo}")  # Should be True
    
    # Redo the delete
    if can_redo:
        command_handler.redo()
        print(f"After redo: {len(section.seats)}")  # Should be 2
    
    print("OK: Delete rows undo/redo working!")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("UNDO/REDO WIRING TEST SUITE")
    print("="*50)
    
    try:
        test_delete_seats_undo_redo()
        test_add_rows_bulk_undo_redo()
        test_delete_rows_undo_redo()
        
        print("\n" + "="*50)
        print("ALL TESTS PASSED - OK")
        print("="*50 + "\n")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
