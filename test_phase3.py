"""Functional test for Phase 3 - Commands and Handlers."""

from src.application import (
    CommandHandler, Result, ValidationErrors,
    AddSectionCommand, DeleteSectionCommand, RenameSectionCommand,
    CloneSectionCommand, MergeSectionsCommand,
    AddSeatCommand, DeleteSeatCommand, DeleteRowCommand, DeleteSeatsCommand
)
from src.domain.models import SeatingPlan, Section

print("=" * 70)
print("PHASE 3: COMMANDS & HANDLERS - FUNCTIONAL TEST")
print("=" * 70)

# Test 1: Result Type
print("\n[1] Testing Result Type")
result_success = Result.success(42)
assert result_success.is_success()
assert not result_success.is_failure()
assert result_success.get_value() == 42
print("  ✓ Result.success() works")

result_failure = Result.failure("Error message")
assert not result_failure.is_success()
assert result_failure.is_failure()
assert result_failure.get_error() == "Error message"
print("  ✓ Result.failure() works")

# Test 2: ValidationErrors
print("\n[2] Testing ValidationErrors")
errors = ValidationErrors()
assert errors.is_empty()
errors.add("Error 1")
assert not errors.is_empty()
errors.add("Error 2")
assert len(errors.errors) == 2
print("  ✓ ValidationErrors collects errors")

# Test 3: Section Commands
print("\n[3] Testing Section Commands")
sp = SeatingPlan("Test Plan")
handler = CommandHandler()

# AddSectionCommand
add_cmd = AddSectionCommand(sp, "Balcony", is_ga=False)
handler.execute(add_cmd)
assert "Balcony" in sp.sections
assert handler.can_undo()
print("  ✓ AddSectionCommand executed")

# Undo
handler.undo()
assert "Balcony" not in sp.sections
assert not handler.can_undo()
assert handler.can_redo()
print("  ✓ Undo works")

# Redo
handler.redo()
assert "Balcony" in sp.sections
assert handler.can_undo()
assert not handler.can_redo()
print("  ✓ Redo works")

# Test 4: Multiple Commands
print("\n[4] Testing Multiple Commands")
add_section2 = AddSectionCommand(sp, "Orchestra", is_ga=False)
handler.execute(add_section2)
assert "Orchestra" in sp.sections

rename_cmd = RenameSectionCommand(sp, "Orchestra", "Main Floor")
handler.execute(rename_cmd)
assert "Main Floor" in sp.sections
assert "Orchestra" not in sp.sections
assert len(sp.sections) == 2
print("  ✓ Multiple commands work in sequence")

# Test 5: Undo History
print("\n[5] Testing Undo History")
assert handler.can_undo()
undo_desc = handler.get_undo_description()
print(f"  Next undo: '{undo_desc}'")

# Current state: Balcony, Orchestra renamed to Main Floor
assert "Balcony" in sp.sections
assert "Main Floor" in sp.sections

# Undo rename
handler.undo()
assert "Orchestra" in sp.sections and "Main Floor" not in sp.sections

# Undo add orchestra
handler.undo()
assert "Orchestra" not in sp.sections and "Balcony" in sp.sections

# Undo add balcony
handler.undo()
assert "Balcony" not in sp.sections

# Redo add balcony
handler.redo()
assert "Balcony" in sp.sections

# Redo add orchestra
handler.redo()
assert "Orchestra" in sp.sections

# Redo rename
handler.redo()
assert "Main Floor" in sp.sections and "Orchestra" not in sp.sections

print("  ✓ Undo history maintains order")

# Test 6: Clone Command
print("\n[6] Testing CloneSectionCommand")
sp.add_section("Regular")
clone_cmd = CloneSectionCommand(sp, "Regular", "Regular 2")
handler.execute(clone_cmd)
assert "Regular 2" in sp.sections
print("  ✓ CloneSectionCommand works")

handler.undo()
assert "Regular 2" not in sp.sections
print("  ✓ Clone undo works")

# Test 7: Merge Command
print("\n[7] Testing MergeSectionsCommand")
sp.add_section("Section A")
sp.add_section("Section B")
sp.sections["Section A"].add_seat("1", "A")
sp.sections["Section B"].add_seat("1", "B")

merge_cmd = MergeSectionsCommand(sp, ["Section A", "Section B"], "Merged")
handler.execute(merge_cmd)
assert "Merged" in sp.sections
assert "1-A" in sp.sections["Merged"].seats
assert "1-B" in sp.sections["Merged"].seats
print("  ✓ MergeSectionsCommand works")

handler.undo()
assert "Section A" in sp.sections
assert "Section B" in sp.sections
assert "Merged" not in sp.sections
print("  ✓ Merge undo restores sections")

# Test 8: Seat Commands
print("\n[8] Testing Seat Commands")
section = sp.sections["Balcony"]
add_seat_cmd = AddSeatCommand(section, "1", "A")
handler.execute(add_seat_cmd)
assert "1-A" in section.seats
print("  ✓ AddSeatCommand works")

delete_seat_cmd = DeleteSeatCommand(section, "1", "A")
handler.execute(delete_seat_cmd)
assert "1-A" not in section.seats
handler.undo()
assert "1-A" in section.seats
print("  ✓ DeleteSeatCommand undo/redo works")

# Test 9: Multiple Seats
print("\n[9] Testing DeleteSeatsCommand")
section.add_seat("2", "A")
section.add_seat("2", "B")
section.add_seat("2", "C")
assert len(section.seats) == 4  # 1-A was restored

delete_seats_cmd = DeleteSeatsCommand(section, ["2-A", "2-B"])
handler.execute(delete_seats_cmd)
assert len(section.seats) == 2
assert "2-A" not in section.seats
assert "2-B" not in section.seats
assert "2-C" in section.seats

handler.undo()
assert len(section.seats) == 4
print("  ✓ DeleteSeatsCommand works")

# Test 10: Command Callbacks
print("\n[10] Testing Command Callbacks")
callback_calls = []

def on_executed(cmd):
    callback_calls.append(('executed', cmd.description))

handler.on_command_executed = on_executed
test_cmd = AddSectionCommand(sp, "Callback Test")
handler.execute(test_cmd)
assert len(callback_calls) == 1
assert callback_calls[0] == ('executed', "Add section 'Callback Test'")
print("  ✓ Command callbacks work")

# Test 11: Handler State
print("\n[11] Testing Handler State")
sp2 = SeatingPlan("Plan 2")
handler2 = CommandHandler(max_history=50)
for i in range(60):
    cmd = AddSectionCommand(sp2, f"Section {i}")
    handler2.execute(cmd)

# History should be capped at 50
assert len(handler2.undo_stack) == 50
print("  ✓ Max history limit works")

print("\n" + "=" * 70)
print("✅ ALL PHASE 3 TESTS PASSED!")
print("=" * 70)
print("\nSummary:")
print("  ✓ Result type for success/failure")
print("  ✓ ValidationErrors for error collection")
print("  ✓ Command base class and execution")
print("  ✓ CommandHandler with undo/redo")
print("  ✓ Section CRUD commands")
print("  ✓ Seat manipulation commands")
print("  ✓ Multiple command sequencing")
print("  ✓ Command callbacks")
print("  ✓ History size limits")
