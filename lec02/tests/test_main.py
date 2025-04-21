import os
import json
import unittest
from unittest.mock import patch
from lec02.app.main import app


class MainAppTestCase(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        self.test_dir = "tests/test_output"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        # Clean up test directory
        for f in os.listdir(self.test_dir):
            file_path = os.path.join(self.test_dir, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir(self.test_dir)

    @patch("lec02.app.main.fetch_data_from_api")
    def test_fetch_sales_success(self, mock_fetch):
        mock_fetch.side_effect = [
            [{"id": 1, "item": "apple"}],
            []
        ]

        response = self.client.post("/", json={
            "raw_dir": self.test_dir,
            "date": "2022-08-09"
        })

        self.assertEqual(response.status_code, 201)
        self.assertIn(b"Sales data fetched and saved successfully", response.data)

        expected_file = os.path.join(self.test_dir, "sales_2022-08-09_1.json")
        self.assertTrue(os.path.exists(expected_file))

        with open(expected_file, "r") as f:
            data = json.load(f)
            self.assertEqual(data[0]["item"], "apple")

    def test_fetch_sales_missing_raw_dir(self):
        response = self.client.post("/", json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Missing raw_dir", response.data)


if __name__ == "__main__":
    unittest.main()
