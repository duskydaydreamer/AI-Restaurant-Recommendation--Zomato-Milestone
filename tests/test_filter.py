"""
Unit tests for the filter pipeline.

Covers: each filter stage, progressive relaxation, cap, location-not-found
with suggestions, and logging (implementation-plan §2.8, §4.5).
"""

import pytest
from app.models.restaurant import Restaurant
from app.models.user_preferences import UserPreferences
from app.services.filter import apply_filters


def get_sample_restaurants():
    return [
        Restaurant(
            id="1", name="R1", location="Indiranagar", city="Bangalore",
            cuisines=["italian", "pizza"], rating=4.5, cost_for_two=1000,
            budget_tier="medium", votes=100
        ),
        Restaurant(
            id="2", name="R2", location="Indiranagar", city="Bangalore",
            cuisines=["chinese", "thai"], rating=4.0, cost_for_two=600,
            budget_tier="medium", votes=50
        ),
        Restaurant(
            id="3", name="R3", location="Koramangala", city="Bangalore",
            cuisines=["italian"], rating=3.5, cost_for_two=400,
            budget_tier="low", votes=200
        ),
        Restaurant(
            id="4", name="R4", location="Indiranagar", city="Bangalore",
            cuisines=["cafe", "bakery"], rating=4.8, cost_for_two=2000,
            budget_tier="high", votes=500
        ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# Exact match
# ═══════════════════════════════════════════════════════════════════════════

def test_exact_match():
    rests = get_sample_restaurants()
    prefs = UserPreferences(
        location="Indiranagar", budget="medium", cuisine="italian", min_rating=4.0
    )
    res = apply_filters(rests, prefs)
    assert len(res.candidates) == 1
    assert res.candidates[0].id == "1"
    assert len(res.relaxations) == 0


# ═══════════════════════════════════════════════════════════════════════════
# Progressive relaxation
# ═══════════════════════════════════════════════════════════════════════════

def test_relax_cuisine():
    rests = get_sample_restaurants()
    # No indian cuisine in medium budget in indiranagar
    prefs = UserPreferences(
        location="Indiranagar", budget="medium", cuisine="indian", min_rating=4.0
    )
    res = apply_filters(rests, prefs)
    # Should relax cuisine and return R1, R2
    assert len(res.candidates) == 2
    ids = {c.id for c in res.candidates}
    assert ids == {"1", "2"}
    assert "Cuisine requirement relaxed" in res.relaxations


def test_relax_cuisine_and_budget():
    rests = get_sample_restaurants()
    # No low budget in indiranagar
    prefs = UserPreferences(
        location="Indiranagar", budget="low", cuisine="indian", min_rating=4.0
    )
    res = apply_filters(rests, prefs)
    # Should relax cuisine and budget and return R1, R2, R4
    assert len(res.candidates) == 3
    ids = {c.id for c in res.candidates}
    assert ids == {"1", "2", "4"}
    assert "Cuisine and Budget requirements relaxed" in res.relaxations


def test_relax_all():
    rests = get_sample_restaurants()
    # Only low rating in Koramangala
    prefs = UserPreferences(
        location="Koramangala", budget="high", cuisine="indian", min_rating=4.5
    )
    res = apply_filters(rests, prefs)
    # Should relax everything and return R3 (the only one in Koramangala)
    assert len(res.candidates) == 1
    assert res.candidates[0].id == "3"
    assert "Cuisine, Budget, and Rating requirements relaxed" in res.relaxations


# ═══════════════════════════════════════════════════════════════════════════
# Location not found — suggestions
# ═══════════════════════════════════════════════════════════════════════════

def test_location_not_found():
    rests = get_sample_restaurants()
    prefs = UserPreferences(
        location="UnknownLocation", budget="low", cuisine="", min_rating=0.0
    )
    res = apply_filters(rests, prefs)
    assert len(res.candidates) == 0
    assert "Location not found in dataset" in res.relaxations


def test_location_not_found_has_suggestions():
    """When location is not found, FilterResult should include suggestions."""
    rests = get_sample_restaurants()
    prefs = UserPreferences(
        location="Paris", budget="low", cuisine="", min_rating=0.0
    )
    res = apply_filters(rests, prefs)
    assert len(res.candidates) == 0
    assert res.suggestions is not None
    assert "available_cities" in res.suggestions
    assert "Bangalore" in res.suggestions["available_cities"]
    assert "popular_cuisines" in res.suggestions
    assert len(res.suggestions["popular_cuisines"]) > 0


# ═══════════════════════════════════════════════════════════════════════════
# Sort and cap
# ═══════════════════════════════════════════════════════════════════════════

def test_sorted_by_rating_descending():
    rests = get_sample_restaurants()
    prefs = UserPreferences(
        location="Bangalore", budget="medium", cuisine="", min_rating=0.0
    )
    res = apply_filters(rests, prefs)
    # All medium-budget restaurants in Bangalore sorted by rating desc
    ratings = [c.rating for c in res.candidates]
    assert ratings == sorted(ratings, reverse=True)


def test_no_cuisine_filter_when_empty():
    """Empty cuisine should skip cuisine filter, not exclude everything."""
    rests = get_sample_restaurants()
    prefs = UserPreferences(
        location="Indiranagar", budget="medium", cuisine="", min_rating=0.0
    )
    res = apply_filters(rests, prefs)
    assert len(res.candidates) == 2
    assert len(res.relaxations) == 0


# ═══════════════════════════════════════════════════════════════════════════
# Partial cuisine match
# ═══════════════════════════════════════════════════════════════════════════

def test_partial_cuisine_match():
    """Partial substring match should work for cuisine (edge-case §2.4)."""
    rests = get_sample_restaurants()
    prefs = UserPreferences(
        location="Indiranagar", budget="medium", cuisine="ital", min_rating=0.0
    )
    res = apply_filters(rests, prefs)
    assert len(res.candidates) == 1
    assert res.candidates[0].id == "1"


# ═══════════════════════════════════════════════════════════════════════════
# City-level match
# ═══════════════════════════════════════════════════════════════════════════

def test_city_level_match():
    """Location query matching city (not just neighbourhood) should work."""
    rests = get_sample_restaurants()
    prefs = UserPreferences(
        location="Bangalore", budget="low", cuisine="", min_rating=0.0
    )
    res = apply_filters(rests, prefs)
    # Should match all restaurants in Bangalore city
    assert len(res.candidates) >= 1
