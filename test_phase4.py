"""Phase 4: Application Services Layer - Functional Tests"""

from src.domain.models.seating_plan import SeatingPlan
from src.application.handlers import CommandHandler
from src.application.services import (
    SeatingPlanService,
    SectionService,
    SeatService,
)


def test_phase4():
    """Test Phase 4 services layer implementation."""
    
    print("=" * 70)
    print("PHASE 4: APPLICATION SERVICES LAYER - FUNCTIONAL TEST")
    print("=" * 70)
    
    # Setup
    sp = SeatingPlan("Test Plan")
    handler = CommandHandler()
    
    # Create main service (which provides section and seat services)
    main_service = SeatingPlanService(sp, handler)
    section_service = main_service.get_section_service()
    seat_service = SeatService(sp, handler)
    
    # Test 1: Section Service - Add Section
    print("\n[1] Testing SectionService.add_section()")
    result = section_service.add_section("Orchestra", is_ga=False)
    assert result.is_success(), f"Expected success, got: {result.error}"
    assert "Orchestra" in sp.sections
    print("  ✓ Add section with validation works")
    
    # Test validation: duplicate name
    result = section_service.add_section("Orchestra", is_ga=False)
    assert result.is_failure(), "Should reject duplicate name"
    assert result.error.has_errors()
    print("  ✓ Validation catches duplicate names")
    
    # Test 2: Section Service - Rename Section
    print("\n[2] Testing SectionService.rename_section()")
    result = section_service.rename_section("Orchestra", "Main Floor")
    if result.is_failure():
        print(f"  Error: {result.error}")
    assert result.is_success(), f"Rename failed: {result.error}"
    assert "Main Floor" in sp.sections
    assert "Orchestra" not in sp.sections
    print("  ✓ Rename section with validation works")
    
    # Test 3: Section Service - Add & Delete
    print("\n[3] Testing SectionService.delete_section()")
    result = section_service.add_section("Balcony", is_ga=False)
    assert result.is_success()
    
    result = section_service.delete_section("Balcony")
    assert result.is_success()
    assert "Balcony" not in sp.sections
    print("  ✓ Delete section works")
    
    # Test 4: Section Service - Clone
    print("\n[4] Testing SectionService.clone_section()")
    result = section_service.add_section("Parquet", is_ga=False)
    assert result.is_success()
    
    result = section_service.clone_section("Parquet", "Parquet Clone")
    assert result.is_success()
    assert "Parquet Clone" in sp.sections
    print("  ✓ Clone section works")
    
    # Test 5: Section Service - Clone Many
    print("\n[5] Testing SectionService.clone_section_many()")
    result = section_service.clone_section_many("Main Floor", 3)
    if result.is_failure():
        print(f"  Error: {result.error}")
    assert result.is_success(), f"Clone many failed: {result.error}"
    cloned_names = result.value
    assert len(cloned_names) == 3
    for name in cloned_names:
        assert name in sp.sections
    print("  ✓ Clone section multiple times works")
    
    # Test 6: Section Service - List sections
    print("\n[6] Testing SectionService queries")
    sections = section_service.get_section_names()
    assert "Main Floor" in sections
    assert "Parquet" in sections
    assert len(sections) > 0
    assert section_service.section_exists("Main Floor")
    assert not section_service.section_exists("NonExistent")
    print(f"  ✓ Section queries work ({len(sections)} sections found)")
    
    # Test 7: Seat Service - Add Seat
    print("\n[7] Testing SeatService.add_seat()")
    result = seat_service.add_seat("Main Floor", "A", "1")
    assert result.is_success()
    assert result.value == ("A", "1")
    assert seat_service.seat_exists("Main Floor", "A", "1")
    print("  ✓ Add seat with validation works")
    
    # Test validation: invalid section
    result = seat_service.add_seat("NonExistent", "A", "1")
    assert result.is_failure()
    print("  ✓ Validation catches invalid section")
    
    # Test 8: Seat Service - Add multiple seats
    print("\n[8] Testing SeatService.add_seat_range()")
    result = seat_service.add_seat_range("Main Floor", "B", "1", "5")
    if result.is_failure():
        print(f"  Error: {result.error}")
    assert result.is_success(), f"Add range failed: {result.error}"
    assert result.value > 0
    assert seat_service.seat_exists("Main Floor", "B", "1")
    assert seat_service.seat_exists("Main Floor", "B", "5")
    print(f"  ✓ Add seat range works ({result.value} seats added)")
    
    # Test 9: Seat Service - Get seats
    print("\n[9] Testing SeatService queries")
    result = seat_service.get_section_seats("Main Floor")
    assert result.is_success()
    seats = result.value
    assert len(seats) > 0
    print(f"  ✓ Get seats works ({len(seats)} seats in Main Floor)")
    
    result = seat_service.get_section_rows("Main Floor")
    assert result.is_success()
    rows = result.value
    assert "A" in rows
    assert "B" in rows
    print(f"  ✓ Get rows works ({len(rows)} rows)")
    
    # Test 10: Seat Service - Delete Seat
    print("\n[10] Testing SeatService.delete_seat()")
    result = seat_service.delete_seat("Main Floor", "A", "1")
    assert result.is_success()
    assert not seat_service.seat_exists("Main Floor", "A", "1")
    print("  ✓ Delete seat works")
    
    # Test 11: Seat Service - Delete Multiple Seats
    print("\n[11] Testing SeatService.delete_seats()")
    # First add some distinct seats we can delete
    seat_service.add_seat("Main Floor", "E", "1")
    seat_service.add_seat("Main Floor", "E", "2")
    seat_service.add_seat("Main Floor", "E", "3")
    assert seat_service.seat_exists("Main Floor", "E", "1")
    assert seat_service.seat_exists("Main Floor", "E", "2")
    
    # Now delete them
    result = seat_service.delete_seats("Main Floor", [("E", "1"), ("E", "2")])
    if result.is_failure():
        print(f"  Error: {result.error}")
    assert result.is_success(), f"Delete seats failed: {result.error}"
    assert not seat_service.seat_exists("Main Floor", "E", "1")
    assert not seat_service.seat_exists("Main Floor", "E", "2")
    assert seat_service.seat_exists("Main Floor", "E", "3")  # Should still exist
    print("  ✓ Delete multiple seats works")
    
    # Test 12: Seat Service - Delete Row
    print("\n[12] Testing SeatService.delete_row()")
    # Add a row first
    seat_service.add_seat_range("Main Floor", "C", "1", "10")
    result = seat_service.delete_row("Main Floor", "C")
    assert result.is_success()
    result = seat_service.get_section_rows("Main Floor")
    assert "C" not in result.value
    print("  ✓ Delete row works")
    
    # Test 13: SeatingPlanService - Plan Info
    print("\n[13] Testing SeatingPlanService.get_plan_info()")
    info = main_service.get_plan_info()
    assert info["name"] == "Test Plan"
    assert info["sections"] > 0
    assert info["total_seats"] > 0
    print(f"  ✓ Plan info: {info['sections']} sections, {info['total_seats']} seats")
    
    # Test 14: SeatingPlanService - Undo/Redo
    print("\n[14] Testing SeatingPlanService.undo()/redo()")
    initial_sections = len(sp.sections)
    
    section_service.add_section("Test Section", is_ga=False)
    assert len(sp.sections) == initial_sections + 1
    
    result = main_service.undo()
    assert result.is_success()
    assert len(sp.sections) == initial_sections
    print("  ✓ Undo works through service")
    
    result = main_service.redo()
    assert result.is_success()
    assert len(sp.sections) == initial_sections + 1
    print("  ✓ Redo works through service")
    
    # Test 15: SeatingPlanService - State queries
    print("\n[15] Testing SeatingPlanService.can_undo()/can_redo()")
    can_undo = main_service.can_undo()
    can_redo = main_service.can_redo()
    assert isinstance(can_undo, bool)
    assert isinstance(can_redo, bool)
    print(f"  ✓ State queries: can_undo={can_undo}, can_redo={can_redo}")
    
    # Test 16: SeatingPlanService - Create new plan
    print("\n[16] Testing SeatingPlanService.create_new_plan()")
    sp.sections["Keep Me"] = sp.sections.pop("Main Floor")
    assert "Keep Me" in sp.sections
    
    result = main_service.create_new_plan("Fresh Plan")
    assert result.is_success()
    assert len(sp.sections) == 0
    assert sp.name == "Fresh Plan"
    print("  ✓ Create new plan clears existing sections")
    
    print("\n" + "=" * 70)
    print("✅ ALL PHASE 4 TESTS PASSED!")
    print("=" * 70)
    
    print("\nSummary:")
    print("  ✓ SectionService with validation and undo")
    print("  ✓ SeatService for seat-level operations")
    print("  ✓ SeatingPlanService coordinates operations")
    print("  ✓ Result types for error handling")
    print("  ✓ CommandHandler integration")
    print("  ✓ Comprehensive validation")


if __name__ == "__main__":
    test_phase4()
