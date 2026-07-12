from fastapi.testclient import TestClient
from app.api import app

with TestClient(app) as client:
    response = client.post("/api/recommendations", json={
        "location": "BTM",
        "budget": "medium",
        "cuisine": "",
        "min_rating": 4.5,
        "additional_preferences": "",
        "top_k": 5
    })

    print("Status Code:", response.status_code)
    try:
        print("Response:", response.json())
    except Exception as e:
        print("Error parsing json:", e)
        print("Raw text:", response.text)
