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
