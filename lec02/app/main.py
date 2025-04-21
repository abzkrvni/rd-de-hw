import os
import json
import requests
from flask import Flask, request
from dotenv import load_dotenv
from typing import Dict, Optional


# Load variables
load_dotenv()

# Flask Server
app = Flask(__name__)

# API Configuration
API_URL = "https://fake-api-vycpfa6oca-uc.a.run.app/"
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
if not AUTH_TOKEN:
    raise ValueError("AUTH_TOKEN is not set in environment variables")

def fetch_data_from_api(date: str, page: int = 1) -> Dict:
    """Fetching data via API"""
    headers = {
        'Authorization': AUTH_TOKEN
    }
    response = requests.get(f"{API_URL}/sales?date={date}&page={page}", headers=headers)
    response.raise_for_status()
    return response.json()

def save_sales_data(data: Dict, file_path: str) -> None:
    """Saving as file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f)

@app.route('/', methods=['POST'])
def fetch_sales() -> str:
    raw_dir: Optional[str] = request.json.get("raw_dir")
    if not raw_dir:
        return "Missing raw_dir", 400

    # Idempotency
    for filename in os.listdir(raw_dir):
        file_path = os.path.join(raw_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    date: str = request.json.get("date", "2022-08-09")
    page: int = 1
    while True:
        try:
            sales_data = fetch_data_from_api(date, page)
            if not sales_data:
                break
            file_name = f"sales_{date}_{page}.json"
            file_path = os.path.join(raw_dir, file_name)
            save_sales_data(sales_data, file_path)
            page += 1
        except Exception as e:
            
            print(f"Error on page {page}: {e}")
            break

    return "Sales data fetched and saved successfully", 201

if __name__ == '__main__':
    app.run(port=8081)
