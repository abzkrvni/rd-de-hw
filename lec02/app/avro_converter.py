import os
import json
import fastavro
from flask import Flask, request
from dotenv import load_dotenv
from typing import Optional


# Env variables
load_dotenv()

# Flask server
app = Flask(__name__)


def convert_json_to_avro(json_file: str, avro_file: str) -> None:
    """Convert JSON to Avro"""
    with open(json_file, 'r') as f:
        data = json.load(f)

        schema = {
            "type": "record",
            "name": "SalesRecord",
            "fields": [
                {"name": "client", "type": "string"},
                {"name": "purchase_date", "type": "string"},
                {"name": "product", "type": "string"},
                {"name": "price", "type": "int"}
            ]
        }

    with open(avro_file, 'wb') as f:
        writer = fastavro.writer(f, schema, data)


@app.route('/', methods=['POST'])
def convert_sales() -> str:
    raw_dir: Optional[str] = request.json.get("raw_dir")
    stg_dir: Optional[str] = request.json.get("stg_dir")

    if not raw_dir or not stg_dir:
        return "Missing parameters", 400

    # Idempotency
    for filename in os.listdir(stg_dir):
        file_path = os.path.join(stg_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    for filename in os.listdir(raw_dir):
        if filename.endswith('.json'):
            json_file = os.path.join(raw_dir, filename)
            avro_file = os.path.join(stg_dir, filename.replace('.json', '.avro'))
            convert_json_to_avro(json_file, avro_file)

    return "Sales data converted to Avro format", 201


if __name__ == '__main__':
    app.run(port=8082)
