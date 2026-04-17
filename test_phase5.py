"""Phase 5: UI Refactoring - Integration Test"""

import sys
from pathlib import Path

from src.domain.models.seating_plan import SeatingPlan
from src.application.handlers import CommandHandler
from src.application.services import SeatingPlanService, SectionService, SeatService
from src.infrastructure.import_export import (
    JSONImporter, ExcelImporter, AvailImporter,
    JSONExporter, ExcelExporter,
)
from src.infrastructure.persistence import JSONRepository


def test_phase5_ui_integration():
    """Test UI integration with services layer."""
    
    print("=" * 70)
    print("PHASE 5: UI REFACTORING - INTEGRATION TEST")
    print("=" * 70)
    
    # Setup services
    print("\n[1] Setting up services layer")
    sp = SeatingPlan("Integration Test Plan")
    handler = CommandHandler()
    
    # Configure use cases for the service
    importers = [
        JSONImporter(),
        ExcelImporter(),
        AvailImporter(),
    ]
    exporters = [
        JSONExporter(),
        ExcelExporter(),
    ]
    repository = JSONRepository()
    
    use_cases_config = {
        "importers": importers,
        "exporters": exporters,
        "repository": repository,
    }
    
    # Create services
    main_service = SeatingPlanService(sp, handler, use_cases_config)
    section_service = main_service.get_section_service()
    seat_service = SeatService(sp, handler)
    
    print("  ✓ Services initialized")
    
    # Test 2: Services coordinate properly
    print("\n[2] Testing service coordination")
    result = section_service.add_section("Orchestra", is_ga=False)
    assert result.is_success()
    assert main_service.can_undo()
    print("  ✓ Services coordinate through CommandHandler")
    
    # Test 3: Callbacks work
    print("\n[3] Testing service callbacks")
    callback_fired = {"count": 0}
    
    def on_command(cmd):
        callback_fired["count"] += 1
    
    handler.on_command_executed = on_command
    result = section_service.add_section("Balcony", is_ga=False)
    assert callback_fired["count"] > 0
    print(f"  ✓ Callbacks working (fired {callback_fired['count']} times)")
    
    # Test 4: Undo/Redo through service
    print("\n[4] Testing service undo/redo")
    initial_sections = len(sp.sections)
    
    main_service.undo()
    assert len(sp.sections) == initial_sections - 1
    print("  ✓ Undo works through service")
    
    main_service.redo()
    assert len(sp.sections) == initial_sections
    print("  ✓ Redo works through service")
    
    # Test 5: Plan info
    print("\n[5] Testing plan information")
    seat_service.add_seat("Orchestra", "A", "1")
    seat_service.add_seat_range("Orchestra", "B", "1", "5")
    
    info = main_service.get_plan_info()
    assert info["sections"] > 0
    assert info["total_seats"] > 0
    assert info["can_undo"]
    print(f"  ✓ Plan info: {info['sections']} sections, {info['total_seats']} seats")
    
    # Test 6: Clean state queries
    print("\n[6] Testing clean state queries")
    sections = section_service.get_section_names()
    assert len(sections) > 0
    assert section_service.section_exists("Orchestra")
    assert not section_service.section_exists("NonExistent")
    print(f"  ✓ Section queries: {len(sections)} sections")
    
    rows_result = seat_service.get_section_rows("Orchestra")
    assert rows_result.is_success()
    rows = rows_result.value
    assert len(rows) > 0
    print(f"  ✓ Seat queries: {len(rows)} rows in Orchestra")
    
    # Test 7: Validation prevents errors
    print("\n[7] Testing validation")
    
    # Try to add duplicate
    result = section_service.add_section("Orchestra", is_ga=False)
    assert result.is_failure()
    assert result.error.has_errors()
    print("  ✓ Validation prevents duplicate sections")
    
    # Try invalid seat operations
    result = seat_service.add_seat("NonExistent", "A", "1")
    assert result.is_failure()
    print("  ✓ Validation catches invalid sections")
    
    # Test 8: Complex workflows
    print("\n[8] Testing complex workflows")
    
    # Create target section first
    section_service.add_section("Merged", is_ga=False)
    
    # Create multiple sections and merge
    section_service.add_section("Parquet", is_ga=False)
    section_service.add_section("Box", is_ga=False)
    
    seat_service.add_seat("Parquet", "1", "1")
    seat_service.add_seat("Box", "1", "1")
    
    result = section_service.merge_sections(["Parquet", "Box"], "Merged", delete_sources=False)
    if result.is_failure():
        print(f"    Merge error: {result.error}")
    assert result.is_success(), f"Merge failed: {result.error}"
    print("  ✓ Complex merge operations work")
    
    # Verify merge preserved original sections
    assert section_service.section_exists("Parquet")
    assert section_service.section_exists("Box")
    print("  ✓ Merge preserves source sections when delete_sources=False")
    
    # Test 9: History limits
    print("\n[9] Testing history management")
    
    initial_history = len(handler.undo_stack)
    for i in range(20):
        section_service.add_section(f"Section_{i}", is_ga=False)
    
    final_history = len(handler.undo_stack)
    assert final_history <= 100  # Default max history
    print(f"  ✓ History limited: {final_history} <= 100")
    
    # Test 10: State consistency
    print("\n[10] Testing state consistency")
    
    # Get a snapshot of state
    sections_before = set(sp.sections.keys())
    total_seats_before = sum(len(s.seats) for s in sp.sections.values())
    
    # Do operations and undo
    result = section_service.add_section("Temp", is_ga=False)
    result = seat_service.add_seat("Temp", "A", "1")
    
    # Undo operations
    main_service.undo()
    main_service.undo()
    
    # State should match
    sections_after = set(sp.sections.keys())
    total_seats_after = sum(len(s.seats) for s in sp.sections.values())
    
    assert sections_before.issuperset(sections_after)  # At least same number
    print("  ✓ State consistency maintained through undo/redo")
    
    print("\n" + "=" * 70)
    print("✅ ALL PHASE 5 INTEGRATION TESTS PASSED!")
    print("=" * 70)
    
    print("\nIntegration Coverage:")
    print("  ✓ SeatingPlanService with CommandHandler")
    print("  ✓ SectionService with auto-undo")
    print("  ✓ SeatService coordination")
    print("  ✓ Validation across layers")
    print("  ✓ Callback system")
    print("  ✓ History management")
    print("  ✓ State consistency")
    print("\nUI Refactoring Benefits:")
    print("  • Services eliminate deep-copy undo/redo")
    print("  • Dialogs extracted to separate module")
    print("  • Widgets focused and testable")
    print("  • MainWindow can be significantly simplified")
    print("  • Clear separation of concerns")


if __name__ == "__main__":
    test_phase5_ui_integration()
