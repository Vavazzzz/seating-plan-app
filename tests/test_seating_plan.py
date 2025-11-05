from src.models.seating_plan import SeatingPlan
from src.models.section import Section
from src.models.seat import Seat
import unittest

class TestSeatingPlan(unittest.TestCase):

    def setUp(self):
        self.seating_plan = SeatingPlan()

    def test_add_section(self):
        self.seating_plan.add_section("A")
        self.assertIn("A", self.seating_plan.sections)

    def test_delete_section(self):
        self.seating_plan.add_section("A")
        self.seating_plan.delete_section("A")
        self.assertNotIn("A", self.seating_plan.sections)

    def test_add_seat_to_section(self):
        self.seating_plan.add_section("A")
        section = self.seating_plan.sections["A"]
        section.add_seat("1", "1")
        self.assertIn(("1", "1"), section.seats)

    def test_delete_seat_from_section(self):
        self.seating_plan.add_section("A")
        section = self.seating_plan.sections["A"]
        section.add_seat("1", "1")
        section.delete_seat("1", "1")
        self.assertNotIn(("1", "1"), section.seats)

    def test_export_to_json(self):
        self.seating_plan.add_section("A")
        section = self.seating_plan.sections["A"]
        section.add_seat("1", "1")
        json_data = self.seating_plan.to_dict()
        self.assertIsInstance(json_data, dict)

    def test_import_from_json(self):
        self.seating_plan.add_section("A")
        section = self.seating_plan.sections["A"]
        section.add_seat("1", "1")
        json_data = self.seating_plan.to_dict()
        
        new_seating_plan = SeatingPlan()
        new_seating_plan.from_dict(json_data)
        self.assertIn("A", new_seating_plan.sections)
        self.assertIn(("1", "1"), new_seating_plan.sections["A"].seats)

if __name__ == '__main__':
    unittest.main()