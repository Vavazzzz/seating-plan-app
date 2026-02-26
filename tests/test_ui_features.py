"""Tests for UI features that affect the model."""

from src.models.seating_plan import SeatingPlan
from src.models.section import Section


def test_reorder_sections_via_dict_recreation():
    """Test reordering sections as done in drag & drop feature."""
    sp = SeatingPlan("UI Test")
    sp.add_section("Section A")
    sp.add_section("Section B")
    sp.add_section("Section C")
    
    # Add some seats to each
    for section_name in ["Section A", "Section B", "Section C"]:
        sp.sections[section_name].add_seat("1", "1")
        sp.sections[section_name].add_seat("1", "2")
    
    # Simulate drag & drop: reorder from [A, B, C] to [C, A, B]
    new_order = ["Section C", "Section A", "Section B"]
    new_sections = {}
    for name in new_order:
        if name in sp.sections:
            new_sections[name] = sp.sections[name]
    sp.sections = new_sections
    
    # Verify order
    assert list(sp.sections.keys()) == ["Section C", "Section A", "Section B"]
    
    # Verify data integrity
    for section_name in ["Section A", "Section B", "Section C"]:
        assert "1-1" in sp.sections[section_name].seats
        assert "1-2" in sp.sections[section_name].seats


def test_move_seat_maintains_data():
    """Test moving seats between sections preserves data integrity."""
    sp = SeatingPlan()
    sp.add_section("Source")
    sp.add_section("Target")
    
    sp.sections["Source"].add_seat("Row1", "A")
    sp.sections["Source"].add_seat("Row1", "B")
    sp.sections["Source"].add_seat("Row2", "A")
    
    # Move Row1-A from Source to Target
    seat = sp.sections["Source"].seats["Row1-A"]
    sp.sections["Target"].add_seat(seat.row_number, seat.seat_number)
    sp.sections["Source"].delete_seat(seat.row_number, seat.seat_number)
    
    # Verify move
    assert "Row1-A" in sp.sections["Target"].seats
    assert "Row1-A" not in sp.sections["Source"].seats
    assert len(sp.sections["Source"].seats) == 2
    assert len(sp.sections["Target"].seats) == 1


def test_multiple_seat_selection_operations():
    """Test batch operations on multiple selected seats."""
    sp = SeatingPlan()
    sp.add_section("Main")
    sp.add_section("Backup")
    
    # Add seats
    sp.sections["Main"].add_seat("1", "A")
    sp.sections["Main"].add_seat("1", "B")
    sp.sections["Main"].add_seat("2", "A")
    sp.sections["Main"].add_seat("2", "B")
    
    # Simulate selecting Row 1 (seats A and B) and deleting them
    selected_seats = [("1", "A"), ("1", "B")]
    for row, seat in selected_seats:
        sp.sections["Main"].delete_seat(row, seat)
    
    assert "1-A" not in sp.sections["Main"].seats
    assert "1-B" not in sp.sections["Main"].seats
    assert "2-A" in sp.sections["Main"].seats
    assert "2-B" in sp.sections["Main"].seats


def test_context_menu_select_all_in_row():
    """Test selecting all seats in a specific row."""
    s = Section("Test")
    s.add_seat("1", "A")
    s.add_seat("1", "B")
    s.add_seat("1", "C")
    s.add_seat("2", "A")
    
    # Get all seats in row "1"
    row_1_seats = {key: seat for key, seat in s.seats.items() if seat.row_number == "1"}
    
    assert len(row_1_seats) == 3
    assert "1-A" in row_1_seats
    assert "1-B" in row_1_seats
    assert "1-C" in row_1_seats
    assert "2-A" not in row_1_seats


def test_context_menu_delete_selected_seats():
    """Test deleting all selected seats."""
    s = Section("Test")
    s.add_seat("1", "A")
    s.add_seat("1", "B")
    s.add_seat("2", "A")
    
    # Simulate selecting and deleting seats 1-A and 1-B
    selected_to_delete = ["1-A", "1-B"]
    for seat_key in selected_to_delete:
        if seat_key in s.seats:
            seat_obj = s.seats[seat_key]
            s.delete_seat(seat_obj.row_number, seat_obj.seat_number)
    
    assert "1-A" not in s.seats
    assert "1-B" not in s.seats
    assert "2-A" in s.seats


def test_context_menu_delete_selected_rows():
    """Test deleting entire rows when seats are selected."""
    s = Section("Test")
    s.add_seat("1", "A")
    s.add_seat("1", "B")
    s.add_seat("2", "A")
    s.add_seat("2", "B")
    s.add_seat("3", "A")
    
    # Get rows containing selected seats
    selected_seats = ["1-A", "2-B"]
    rows_to_delete = set()
    for seat_key in selected_seats:
        if seat_key in s.seats:
            rows_to_delete.add(s.seats[seat_key].row_number)
    
    # Delete all rows
    for row in rows_to_delete:
        s.delete_row(row)
    
    assert not any(k.startswith("1-") for k in s.seats.keys())
    assert not any(k.startswith("2-") for k in s.seats.keys())
    assert "3-A" in s.seats


def test_section_order_stability():
    """Test that section order remains stable across operations."""
    sp = SeatingPlan("Stability Test")
    sections = ["VIP", "Orchestra", "Mezzanine", "Balcony"]
    
    for section_name in sections:
        sp.add_section(section_name)
        sp.sections[section_name].add_seat("1", "1")
    
    original_order = list(sp.sections.keys())
    assert original_order == sections
    
    # Perform various operations
    sp.sections["VIP"].add_seat("2", "1")
    sp.sections["Orchestra"].delete_seat("1", "1")
    
    # Order should remain the same
    assert list(sp.sections.keys()) == original_order


def test_reorder_with_different_section_counts():
    """Test reordering works with different numbers of sections."""
    for num_sections in [2, 5, 10]:
        sp = SeatingPlan(f"Test {num_sections}")
        section_names = [f"Section {i}" for i in range(num_sections)]
        
        for name in section_names:
            sp.add_section(name)
        
        # Reverse order
        reversed_order = list(reversed(section_names))
        new_sections = {}
        for name in reversed_order:
            new_sections[name] = sp.sections[name]
        sp.sections = new_sections
        
        assert list(sp.sections.keys()) == reversed_order
