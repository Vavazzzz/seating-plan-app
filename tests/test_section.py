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
