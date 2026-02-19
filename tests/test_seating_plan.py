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
