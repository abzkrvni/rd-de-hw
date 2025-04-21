import os
import json
import unittest
import fastavro
from lec02.app.avro_converter import app


class AvroConverterTestCase(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        self.raw_dir = "tests/raw"
        self.stg_dir = "tests/stg"

        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.stg_dir, exist_ok=True)

        # Sample input JSON file
        sample_data = [
            {
                "client": "Alice",
                "purchase_date": "2023-07-20",
                "product": "Book",
                "price": 25
            }
        ]
        with open(os.path.join(self.raw_dir, "sample.json"), "w") as f:
            json.dump(sample_data, f)

    def tearDown(self):
        for d in [self.raw_dir, self.stg_dir]:
            for f in os.listdir(d):
                os.remove(os.path.join(d, f))
            os.rmdir(d)

    def test_convert_sales_to_avro(self):
        response = self.client.post("/", json={
            "raw_dir": self.raw_dir,
            "stg_dir": self.stg_dir
        })

        self.assertEqual(response.status_code, 201)
        self.assertIn(b"Sales data converted to Avro format", response.data)

        avro_files = [f for f in os.listdir(self.stg_dir) if f.endswith(".avro")]
        self.assertEqual(len(avro_files), 1)

        # Check content of the AVRO file
        avro_path = os.path.join(self.stg_dir, avro_files[0])
        with open(avro_path, "rb") as f:
            reader = fastavro.reader(f)
            records = list(reader)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["client"], "Alice")
        self.assertEqual(records[0]["price"], 25)


if __name__ == "__main__":
    unittest.main()
