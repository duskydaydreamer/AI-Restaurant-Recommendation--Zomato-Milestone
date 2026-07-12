"""
Manual smoke check — GET /api/locations
=========================================
This is NOT a pytest test. Run it directly:

    python tests/manual_checks/manual_locations_check.py

Requires the dataset to be loaded (PARQUET_PATH env var must be set).
"""

from fastapi.testclient import TestClient
from app.api import app

with TestClient(app) as client:
    response = client.get("/api/locations")
    print("GET /api/locations Status Code:", response.status_code)
    try:
        print("Response:", response.json())
    except Exception as e:
        print("Error parsing json:", e)
        print("Raw text:", response.text)
