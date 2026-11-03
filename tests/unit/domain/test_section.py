import pytest

from domain.exceptions import ValidationError
from domain.models.section import Section


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


def test_clone_preserves_ga_flag():
    """Cloning a general admission section must keep is_ga set."""
    ga = Section("Lawn", is_ga=True)
    assert ga.clone().is_ga is True

    reserved = Section("Stalls", is_ga=False)
    assert reserved.clone().is_ga is False


def test_renumber_rows_empty_input_returns_empty_mapping():
    s = Section("A")
    s.add_seat("1", "A")
    assert s.renumber_rows([], "1") == {}
    assert "1-A" in s.seats


def test_renumber_seats_moves_only_selected_seats():
    s = Section("A")
    s.add_seat_range("A", "1", "4")
    moved = s.renumber_seats([("A", "1"), ("A", "2")], "5")
    assert moved == [("A", "1", "5"), ("A", "2", "5")]
    assert set(s.seats) == {"5-1", "5-2", "A-3", "A-4"}
    assert s.seats["5-1"].row_number == "5"


def test_renumber_seats_maps_rows_sequentially():
    s = Section("A")
    s.add_seat("A", "1")
    s.add_seat("C", "1")
    s.renumber_seats([("A", "1"), ("C", "1")], "1")
    assert set(s.seats) == {"1-1", "2-1"}


def test_renumber_seats_with_prefix():
    s = Section("A")
    s.add_seat("A", "1")
    s.renumber_seats([("A", "1")], "1", add_prefix=True)
    assert set(s.seats) == {"#1-1"}


def test_renumber_seats_conflict_raises_and_leaves_section_unchanged():
    s = Section("A")
    s.add_seat_range("A", "1", "3")
    s.add_seat_range("B", "2", "3")
    with pytest.raises(ValidationError) as exc:
        s.renumber_seats([("A", "1"), ("A", "2"), ("A", "3")], "B")
    assert exc.value.errors == ["B-2", "B-3"]
    assert set(s.seats) == {"A-1", "A-2", "A-3", "B-2", "B-3"}


def test_renumber_seats_into_slots_vacated_by_other_moved_seats():
    s = Section("A")
    s.add_seat("1", "A")
    s.add_seat("2", "A")
    s.renumber_seats([("1", "A"), ("2", "A")], "2")
    assert set(s.seats) == {"2-A", "3-A"}
    assert len(s.seats) == 2


def test_renumber_seats_ignores_missing_seats():
    s = Section("A")
    s.add_seat("1", "A")
    assert s.renumber_seats([("9", "Z")], "1") == []
    assert set(s.seats) == {"1-A"}


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