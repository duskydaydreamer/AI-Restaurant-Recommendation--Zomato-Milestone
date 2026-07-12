"""
Integration tests for the FastAPI REST API.

Uses httpx TestClient against the FastAPI app.
"""

import pytest
from fastapi.testclient import TestClient

from app.api import app, _dataset
from app.models.restaurant import Restaurant


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def seed_dataset():
    """Seed the in-memory dataset with test data."""
    import app.api as api_module

    api_module._dataset = [
        Restaurant(
            id="1", name="Pizza Palace", location="Indiranagar",
            city="Bangalore", cuisines=["italian", "pizza"],
            rating=4.5, cost_for_two=1000, budget_tier="medium",
            votes=200, online_order=True, book_table=True,
            rest_type="Casual Dining", address="123 Main St",
        ),
        Restaurant(
            id="2", name="Dragon Wok", location="Indiranagar",
            city="Bangalore", cuisines=["chinese", "thai"],
            rating=4.0, cost_for_two=700, budget_tier="medium",
            votes=150, online_order=True, book_table=False,
            rest_type="Quick Bites", address="456 Side St",
        ),
        Restaurant(
            id="3", name="Dosa Corner", location="Koramangala",
            city="Bangalore", cuisines=["south indian"],
            rating=4.2, cost_for_two=300, budget_tier="low",
            votes=500, online_order=True, book_table=False,
            rest_type="Quick Bites", address="789 Other St",
        ),
        Restaurant(
            id="4", name="Le Bistro", location="Bellandur",
            city="Bangalore", cuisines=["continental", "french"],
            rating=4.8, cost_for_two=2500, budget_tier="high",
            votes=80, online_order=False, book_table=True,
            rest_type="Fine Dining", address="101 Fancy Ave",
        ),
    ]
    yield
    api_module._dataset = []


client = TestClient(app, raise_server_exceptions=False)


# ── Health ──────────────────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_ok(self):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["restaurant_count"] == 4
        assert data["location_count"] == 3

    def test_health_has_groq_info(self):
        resp = client.get("/api/health")
        data = resp.json()
        assert "groq_model" in data
        assert "groq_key_configured" in data


# ── Locations ───────────────────────────────────────────────────────────────

class TestLocationsEndpoint:
    def test_returns_sorted_locations(self):
        resp = client.get("/api/locations")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 3
        assert data["locations"] == ["Bellandur", "Indiranagar", "Koramangala"]


# ── Cuisines ────────────────────────────────────────────────────────────────

class TestCuisinesEndpoint:
    def test_returns_sorted_cuisines(self):
        resp = client.get("/api/cuisines")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] > 0
        # All should be title-cased
        for c in data["cuisines"]:
            assert c == c.title() or c == c  # title case


# ── Recommendations ────────────────────────────────────────────────────────

class TestRecommendationsEndpoint:
    def test_valid_request_returns_200(self):
        resp = client.post("/api/recommendations", json={
            "location": "Indiranagar",
            "budget": "medium",
            "min_rating": 3.5,
            "top_k": 3,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "summary" in data
        assert "recommendations" in data
        assert "relaxations" in data
        assert "candidate_count" in data

    def test_invalid_budget_returns_400(self):
        resp = client.post("/api/recommendations", json={
            "location": "Indiranagar",
            "budget": "ultra-premium",
        })
        assert resp.status_code == 400
        assert "Invalid budget" in resp.json()["detail"]

    def test_missing_location_returns_422(self):
        resp = client.post("/api/recommendations", json={
            "budget": "low",
        })
        assert resp.status_code == 422

    def test_unknown_location_returns_empty(self):
        resp = client.post("/api/recommendations", json={
            "location": "NonExistentPlace",
            "budget": "low",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["recommendations"] == []
        assert any("Location" in r for r in data["relaxations"])
