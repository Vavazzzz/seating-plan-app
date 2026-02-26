from src.models.seating_plan import SeatingPlan, MergeConflictError


def test_add_and_delete_section():
    sp = SeatingPlan("Test")
    sp.add_section("A")
    assert "A" in sp.sections
    sp.delete_section("A")
    assert "A" not in sp.sections


def test_add_seat_to_section():
    sp = SeatingPlan()
    sp.add_section("A")
    sec = sp.sections["A"]
    sec.add_seat("1", "A")
    assert "1-A" in sec.seats


def test_to_dict_and_from_dict_roundtrip():
    sp = SeatingPlan("Roundtrip")
    sp.add_section("A")
    sp.sections["A"].add_seat("1", "A")
    data = sp.to_dict()
    new = SeatingPlan()
    new.from_dict(data)
    assert "A" in new.sections
    assert "1-A" in new.sections["A"].seats


def test_clone_section_and_independence():
    sp = SeatingPlan()
    sp.add_section("A")
    sp.sections["A"].add_seat("1", "A")
    sp.clone_section("A", "A copy")
    assert "A copy" in sp.sections
    # modify clone and ensure original unchanged
    sp.sections["A copy"].add_seat("2", "B")
    assert "2-B" in sp.sections["A copy"].seats
    assert "2-B" not in sp.sections["A"].seats


def test_clone_section_many_creates_requested_count():
    sp = SeatingPlan()
    sp.add_section("A")
    created = sp.clone_section_many("A", 3)
    assert len(created) == 3
    for name in created:
        assert name in sp.sections


def test_merge_sections_combines_seats():
    sp = SeatingPlan()
    sp.add_section("S1")
    sp.add_section("S2")
    sp.sections["S1"].add_seat("1", "A")
    sp.sections["S2"].add_seat("2", "B")
    sp.merge_sections(["S1", "S2"], "Merged")
    assert "Merged" in sp.sections
    assert "1-A" in sp.sections["Merged"].seats
    assert "2-B" in sp.sections["Merged"].seats


def test_merge_sections_conflict_raises():
    sp = SeatingPlan()
    sp.add_section("S1")
    sp.add_section("S2")
    sp.sections["S1"].add_seat("1", "A")
    sp.sections["S2"].add_seat("1", "A")
    try:
        sp.merge_sections(["S1", "S2"], "Merged")
        assert False, "Expected MergeConflictError"
    except MergeConflictError:
        assert True

def test_section_order_preserved():
    """Test that sections maintain insertion order."""
    sp = SeatingPlan("Order Test")
    sp.add_section("Balcony")
    sp.add_section("Orchestra")
    sp.add_section("Mezzanine")
    
    section_names = list(sp.sections.keys())
    assert section_names == ["Balcony", "Orchestra", "Mezzanine"]


def test_sections_reordering():
    """Test reordering sections by recreating the sections dict."""
    sp = SeatingPlan("Reorder Test")
    sp.add_section("A")
    sp.add_section("B")
    sp.add_section("C")
    sp.sections["A"].add_seat("1", "1")
    sp.sections["B"].add_seat("1", "1")
    sp.sections["C"].add_seat("1", "1")
    
    # Reorder to [C, A, B]
    new_order = ["C", "A", "B"]
    new_sections = {}
    for name in new_order:
        if name in sp.sections:
            new_sections[name] = sp.sections[name]
    sp.sections = new_sections
    
    assert list(sp.sections.keys()) == ["C", "A", "B"]
    # Verify data integrity
    assert "1-1" in sp.sections["A"].seats
    assert "1-1" in sp.sections["B"].seats
    assert "1-1" in sp.sections["C"].seats


def test_move_seat_between_sections():
    """Test moving a seat from one section to another."""
    sp = SeatingPlan()
    sp.add_section("Section1")
    sp.add_section("Section2")
    
    sp.sections["Section1"].add_seat("1", "A")
    sp.sections["Section1"].add_seat("1", "B")
    
    assert "1-A" in sp.sections["Section1"].seats
    assert "1-B" in sp.sections["Section1"].seats
    
    # Move seat 1-A to Section2
    seat = sp.sections["Section1"].seats["1-A"]
    sp.sections["Section2"].add_seat(seat.row_number, seat.seat_number)
    sp.sections["Section1"].delete_seat(seat.row_number, seat.seat_number)
    
    assert "1-A" not in sp.sections["Section1"].seats
    assert "1-A" in sp.sections["Section2"].seats
    assert "1-B" in sp.sections["Section1"].seats


def test_rename_section_preserves_content():
    """Test that renaming a section preserves all seat data."""
    sp = SeatingPlan()
    sp.add_section("OldName")
    sp.sections["OldName"].add_seat("1", "A")
    sp.sections["OldName"].add_seat("1", "B")
    sp.sections["OldName"].add_seat("2", "A")
    
    # Rename section
    sp.rename_section("OldName", "NewName")
    
    assert "OldName" not in sp.sections
    assert "NewName" in sp.sections
    assert len(sp.sections["NewName"].seats) == 3
    assert "1-A" in sp.sections["NewName"].seats
    assert "1-B" in sp.sections["NewName"].seats
    assert "2-A" in sp.sections["NewName"].seats