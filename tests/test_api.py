import unittest

from fastapi.testclient import TestClient
from src.api.main import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "message": "Seating Plan API"})

    def test_list_projects_empty(self):
        response = self.client.get("/api/seatingplans/list")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"projects": []})

    def test_create_new_project(self):
        response = self.client.post("/api/seatingplans/new/testproject")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "testproject")
        self.assertIn("seating_plan", data)

    def test_list_projects_non_empty(self):
        # Create a project first
        self.client.post("/api/seatingplans/new/testproject2")
        response = self.client.get("/api/seatingplans/list")
        self.assertEqual(response.status_code, 200)
        self.assertIn("testproject2", response.json()["projects"])

if __name__ == '__main__':
    unittest.main()