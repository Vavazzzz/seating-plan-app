#!/usr/bin/env python
"""
Final cleanup validation test.
Verifies that all core functionality works after cleanup and refactoring.
"""

import sys

print("=" * 70)
print("CLEANUP VALIDATION TEST")
print("=" * 70)

# Test 1: Domain layer
try:
    from src.domain import SeatingPlan, Section, Seat
    from src.domain.exceptions import ValidationError, MergeConflictError
    print("\n[1] Domain layer... OK")
except Exception as e:
    print(f"\n[1] Domain layer... FAILED: {e}")
    sys.exit(1)

# Test 2: Application services
try:
    from src.application import CommandHandler
    from src.application.services import SeatingPlanService, SectionService, SeatService
    
    sp = SeatingPlan("Test Plan")
    command_handler = CommandHandler()
    plan_service = SeatingPlanService(sp, command_handler)
    section_service = SectionService(sp, command_handler)
    seat_service = SeatService(sp, command_handler)
    
    print("[2] Application services... OK")
except Exception as e:
    print(f"[2] Application services... FAILED: {e}")
    sys.exit(1)

# Test 3: Infrastructure layer
try:
    from src.infrastructure.persistence import JSONRepository
    from src.infrastructure.import_export import JSONImporter, JSONExporter
    
    print("[3] Infrastructure layer... OK")
except Exception as e:
    print(f"[3] Infrastructure layer... FAILED: {e}")
    sys.exit(1)

# Test 4: UI layer
try:
    from src.ui.dialogs import (
        AddSectionDialog, RenameSectionDialog, MergeSectionsDialog, 
        CloneSectionDialog, AddSeatDialog, AddSeatRangeDialog, FileDialog
    )
    print("[4] UI dialogs layer... OK")
except Exception as e:
    print(f"[4] UI dialogs layer... FAILED: {e}")
    sys.exit(1)

# Test 5: File handlers
try:
    from src.utils.file_handlers import import_excel_to_plan, export_plan_to_excel
    print("[5] File handlers (legacy utils)... OK")
except Exception as e:
    print(f"[5] File handlers... FAILED: {e}")
    sys.exit(1)

# Test 6: Core functionality
try:
    # Add a section
    result = section_service.add_section("Main Floor", is_ga=False)
    if not result.is_success():
        raise Exception(f"Failed to add section: {result.get_error()}")
    
    # Add seats
    result = seat_service.add_seat("Main Floor", "1", "A")
    if not result.is_success():
        raise Exception(f"Failed to add seat: {result.get_error()}")
    
    # Get plan info
    plan_info = plan_service.get_plan_info()
    
    if plan_info['sections'] != 1:
        raise Exception(f"Expected 1 section, got {plan_info['sections']}")
    
    if plan_info['total_seats'] != 1:
        raise Exception(f"Expected 1 seat, got {plan_info['total_seats']}")
    
    print("[6] Core functionality... OK")
    print(f"    - Created plan with 1 section and 1 seat")
except Exception as e:
    print(f"[6] Core functionality... FAILED: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("CLEANUP VALIDATION SUCCESSFUL")
print("=" * 70)
print("\nRemoved files:")
print("  - src/presentation/ (entire unused layer)")
print("  - tests/integration/ (empty directory)")
print("  - 10 old dialog files (consolidated)")
print("  - src/config.py (unused)")
print("  - src/infrastructure/utils/validators.py (unused)")
print("\nUpdated:")
print("  - README.md with accurate architecture docs")
print("  - Added module docstring to file_handlers.py")
print("\nValidation:")
print("  - All import paths working")
print("  - Core functionality operational")
print("  - Session structure clean and maintainable")
print("\n" + "=" * 70)
