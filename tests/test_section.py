from src.models.section import Section


def test_add_and_delete_seat():
    s = Section("A")
    s.add_seat("1", "A")
    assert "1-A" in s.seats
    s.delete_seat("1", "A")
    assert "1-A" not in s.seats


def test_delete_row_removes_all_row_seats():
    s = Section("A")
    s.add_seat("1", "A")
    s.add_seat("1", "B")
    s.delete_row("1")
    assert not any(k.startswith("1-") for k in s.seats.keys())


def test_rename_section_updates_name():
    s = Section("A")
    s.rename("B")
    assert s.name == "B"


def test_change_seat_number_moves_entry():
    s = Section("A")
    s.add_seat("1", "A")
    assert "1-A" in s.seats
    s.change_seat_number("1", "A", "B")
    assert "1-A" not in s.seats
    assert "1-B" in s.seats


def test_add_seat_range_alpha():
    s = Section("A")
    s.add_seat_range("1", "A", "C")
    assert "1-A" in s.seats
    assert "1-B" in s.seats
    assert "1-C" in s.seats

def test_add_seat_range_numeric():
    """Test adding numeric seat ranges."""
    s = Section("A")
    s.add_seat_range("1", "1", "3")
    assert "1-1" in s.seats
    assert "1-2" in s.seats
    assert "1-3" in s.seats


def test_delete_multiple_seats():
    """Test deleting multiple seats from different rows."""
    s = Section("A")
    s.add_seat("1", "A")
    s.add_seat("1", "B")
    s.add_seat("2", "A")
    s.add_seat("2", "B")
    
    s.delete_seat("1", "A")
    s.delete_seat("2", "B")
    
    assert len(s.seats) == 2
    assert "1-A" not in s.seats
    assert "2-B" not in s.seats
    assert "1-B" in s.seats
    assert "2-A" in s.seats


def test_clone_section():
    """Test cloning a section with all its seats."""
    s1 = Section("Original")
    s1.add_seat("1", "A")
    s1.add_seat("1", "B")
    s1.add_seat("2", "A")
    
    s2 = s1.clone()
    
    # Clone appends "_copy" to the name
    assert s2.name == "Original_copy"
    assert len(s2.seats) == 3
    assert "1-A" in s2.seats
    assert "1-B" in s2.seats
    assert "2-A" in s2.seats
    
    # Modify clone and verify original unchanged
    s2.add_seat("3", "A")
    assert "3-A" not in s1.seats
    assert "3-A" in s2.seats


def test_section_seat_count():
    """Test getting accurate seat count."""
    s = Section("A")
    assert len(s.seats) == 0
    
    s.add_seat("1", "A")
    s.add_seat("1", "B")
    s.add_seat("2", "A")
    assert len(s.seats) == 3
    
    s.delete_seat("1", "A")
    assert len(s.seats) == 2


def test_get_rows_in_section():
    """Test getting all unique rows in a section."""
    s = Section("A")
    s.add_seat("1", "A")
    s.add_seat("1", "B")
    s.add_seat("2", "A")
    s.add_seat("3", "C")
    
    rows = set(seat.row_number for seat in s.seats.values())
    assert rows == {"1", "2", "3"}