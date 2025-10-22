from models.section import Section
import unittest

class TestSection(unittest.TestCase):

    def setUp(self):
        self.section = Section("A")

    def test_add_seat(self):
        self.section.add_seat("1", "A")
        self.assertIn("A1", self.section.seats)

    def test_delete_seat(self):
        self.section.add_seat("1", "A")
        self.section.delete_seat("1", "A")
        self.assertNotIn("A1", self.section.seats)

    def test_delete_row(self):
        self.section.add_seat("1", "A")
        self.section.add_seat("1", "B")
        self.section.delete_row("1")
        self.assertNotIn("A1", self.section.seats)
        self.assertNotIn("B1", self.section.seats)

    def test_rename_section(self):
        self.section.rename("B")
        self.assertEqual(self.section.name, "B")

    def test_change_seat_number(self):
        self.section.add_seat("1", "A")
        self.section.change_seat_number("1", "B")
        self.assertNotIn("A1", self.section.seats)
        self.assertIn("B1", self.section.seats)

    def test_add_seat_range(self):
        self.section.add_seat_range("1", "A", "C")
        self.assertIn("A1", self.section.seats)
        self.assertIn("B1", self.section.seats)
        self.assertIn("C1", self.section.seats)

    def test_delete_seat_range(self):
        self.section.add_seat_range("1", "A", "C")
        self.section.delete_seat_range("1", "A", "B")
        self.assertNotIn("A1", self.section.seats)
        self.assertNotIn("B1", self.section.seats)
        self.assertIn("C1", self.section.seats)

if __name__ == "__main__":
    unittest.main()