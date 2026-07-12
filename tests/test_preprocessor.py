"""
Unit tests for the preprocessor module.

Covers: normalisation, budget tiers, cuisine parsing, rating coercion,
cost parsing, boolean parsing, and end-to-end row preprocessing.

Implementation-plan §1.7
"""

import pytest

from app.data.preprocessor import (
    extract_city_from_row,
    normalise_city,
    normalise_location,
    parse_bool_field,
    parse_cost,
    parse_cuisines,
    parse_dish_liked,
    parse_rating,
    parse_votes,
    preprocess_dataset,
    preprocess_row,
)


# ═══════════════════════════════════════════════════════════════════════════
# City normalisation
# ═══════════════════════════════════════════════════════════════════════════

class TestNormaliseCity:
    def test_alias_bengaluru(self):
        assert normalise_city("Bengaluru") == "Bangalore"

    def test_alias_bangalore(self):
        assert normalise_city("bangalore") == "Bangalore"

    def test_alias_bombay(self):
        assert normalise_city("Bombay") == "Mumbai"

    def test_alias_madras(self):
        assert normalise_city("madras") == "Chennai"

    def test_alias_calcutta(self):
        assert normalise_city("Calcutta") == "Kolkata"

    def test_unknown_city_title_cased(self):
        assert normalise_city("mysore") == "Mysore"

    def test_whitespace_stripped(self):
        assert normalise_city("  Bengaluru  ") == "Bangalore"

    def test_none_returns_unknown(self):
        assert normalise_city(None) == "Unknown"

    def test_empty_string_returns_unknown(self):
        assert normalise_city("") == "Unknown"

    def test_non_string_returns_unknown(self):
        assert normalise_city(123) == "Unknown"


# ═══════════════════════════════════════════════════════════════════════════
# Location normalisation
# ═══════════════════════════════════════════════════════════════════════════

class TestNormaliseLocation:
    def test_title_cases(self):
        assert normalise_location("koramangala") == "Koramangala"

    def test_strips_whitespace(self):
        assert normalise_location("  indiranagar  ") == "Indiranagar"

    def test_none_returns_unknown(self):
        assert normalise_location(None) == "Unknown"


# ═══════════════════════════════════════════════════════════════════════════
# Cuisine parsing
# ═══════════════════════════════════════════════════════════════════════════

class TestParseCuisines:
    def test_basic_split(self):
        assert parse_cuisines("North Indian, Chinese") == [
            "north indian",
            "chinese",
        ]

    def test_deduplication(self):
        assert parse_cuisines("Chinese, North Indian, Chinese") == [
            "chinese",
            "north indian",
        ]

    def test_whitespace_handling(self):
        assert parse_cuisines("  Italian , Thai  ") == ["italian", "thai"]

    def test_empty_string(self):
        assert parse_cuisines("") == []

    def test_none_returns_empty(self):
        assert parse_cuisines(None) == []

    def test_single_cuisine(self):
        assert parse_cuisines("Chinese") == ["chinese"]


# ═══════════════════════════════════════════════════════════════════════════
# Cost parsing
# ═══════════════════════════════════════════════════════════════════════════

class TestParseCost:
    def test_integer(self):
        assert parse_cost(800) == 800.0

    def test_float(self):
        assert parse_cost(1200.5) == 1200.5

    def test_string_plain(self):
        assert parse_cost("800") == 800.0

    def test_string_with_comma(self):
        assert parse_cost("1,200") == 1200.0

    def test_string_with_currency(self):
        assert parse_cost("₹ 1,200") == 1200.0

    def test_negative_clamped(self):
        assert parse_cost(-100) == 0.0

    def test_garbage_returns_zero(self):
        assert parse_cost("not a number") == 0.0

    def test_none_returns_zero(self):
        assert parse_cost(None) == 0.0


# ═══════════════════════════════════════════════════════════════════════════
# Rating parsing
# ═══════════════════════════════════════════════════════════════════════════

class TestParseRating:
    def test_float_value(self):
        assert parse_rating(4.2) == 4.2

    def test_string_value(self):
        assert parse_rating("4.2") == 4.2

    def test_fraction_format(self):
        assert parse_rating("4.1/5") == 4.1

    def test_new_placeholder(self):
        assert parse_rating("NEW") == 0.0

    def test_dash_placeholder(self):
        assert parse_rating("-") == 0.0

    def test_clamped_above_five(self):
        assert parse_rating(6.0) == 5.0

    def test_clamped_below_zero(self):
        assert parse_rating(-1.0) == 0.0

    def test_none_returns_zero(self):
        assert parse_rating(None) == 0.0

    def test_empty_string(self):
        assert parse_rating("") == 0.0


# ═══════════════════════════════════════════════════════════════════════════
# Boolean field parsing
# ═══════════════════════════════════════════════════════════════════════════

class TestParseBoolField:
    def test_yes(self):
        assert parse_bool_field("Yes") is True

    def test_no(self):
        assert parse_bool_field("No") is False

    def test_true_bool(self):
        assert parse_bool_field(True) is True

    def test_false_bool(self):
        assert parse_bool_field(False) is False

    def test_one_string(self):
        assert parse_bool_field("1") is True

    def test_none(self):
        assert parse_bool_field(None) is False


# ═══════════════════════════════════════════════════════════════════════════
# Votes parsing
# ═══════════════════════════════════════════════════════════════════════════

class TestParseVotes:
    def test_integer(self):
        assert parse_votes(1200) == 1200

    def test_string(self):
        assert parse_votes("1,200") == 1200

    def test_float(self):
        assert parse_votes(1200.7) == 1200

    def test_none(self):
        assert parse_votes(None) == 0

    def test_garbage(self):
        assert parse_votes("abc") == 0


# ═══════════════════════════════════════════════════════════════════════════
# Dish liked parsing
# ═══════════════════════════════════════════════════════════════════════════

class TestParseDishLiked:
    def test_split(self):
        assert parse_dish_liked("Biryani, Pasta, Naan") == [
            "Biryani",
            "Pasta",
            "Naan",
        ]

    def test_none(self):
        assert parse_dish_liked(None) == []

    def test_empty(self):
        assert parse_dish_liked("") == []


# ═══════════════════════════════════════════════════════════════════════════
# Budget tier derivation (via config.get_budget_tier)
# ═══════════════════════════════════════════════════════════════════════════

class TestBudgetTier:
    """These test the budget tier derived during preprocessing."""

    def test_low_tier(self):
        row = _make_row(cost="400", rating="4.0", votes="100")
        r = preprocess_row(row, 0)
        assert r is not None
        assert r.budget_tier == "low"

    def test_medium_tier(self):
        row = _make_row(cost="800", rating="4.0", votes="100")
        r = preprocess_row(row, 0)
        assert r is not None
        assert r.budget_tier == "medium"

    def test_high_tier(self):
        row = _make_row(cost="2000", rating="4.0", votes="100")
        r = preprocess_row(row, 0)
        assert r is not None
        assert r.budget_tier == "high"

    def test_boundary_low(self):
        """cost == 500 should be 'low'."""
        row = _make_row(cost="500", rating="4.0", votes="100")
        r = preprocess_row(row, 0)
        assert r is not None
        assert r.budget_tier == "low"

    def test_boundary_medium(self):
        """cost == 1500 should be 'medium'."""
        row = _make_row(cost="1500", rating="4.0", votes="100")
        r = preprocess_row(row, 0)
        assert r is not None
        assert r.budget_tier == "medium"

    def test_boundary_high(self):
        """cost == 1501 should be 'high'."""
        row = _make_row(cost="1501", rating="4.0", votes="100")
        r = preprocess_row(row, 0)
        assert r is not None
        assert r.budget_tier == "high"


# ═══════════════════════════════════════════════════════════════════════════
# City extraction from row
# ═══════════════════════════════════════════════════════════════════════════

class TestExtractCityFromRow:
    def test_extracts_from_url(self):
        row = _make_row()
        assert extract_city_from_row(row) == "Bangalore"

    def test_extracts_from_url_different_city(self):
        row = _make_row(url="https://www.zomato.com/mumbai/some-restaurant")
        assert extract_city_from_row(row) == "Mumbai"

    def test_extracts_from_address_when_no_url(self):
        row = _make_row(url="")
        row["address"] = "123 Test St, Koramangala, Bangalore"
        assert extract_city_from_row(row) == "Bangalore"

    def test_explicit_city_column_takes_precedence(self):
        row = _make_row()
        row["city"] = "Mumbai"  # explicit city column
        assert extract_city_from_row(row) == "Mumbai"

    def test_fallback_to_bangalore(self):
        row = _make_row(url="", address="somewhere unknown")
        assert extract_city_from_row(row) == "Bangalore"


# ═══════════════════════════════════════════════════════════════════════════
# Row-level preprocessing
# ═══════════════════════════════════════════════════════════════════════════

class TestPreprocessRow:
    def test_valid_row(self):
        row = _make_row()
        r = preprocess_row(row, 0)
        assert r is not None
        assert r.name == "Test Restaurant"
        assert r.city == "Bangalore"
        assert r.location == "Koramangala"  # neighbourhood, not city
        assert r.cuisines == ["north indian", "chinese"]
        assert r.rating == 4.2
        assert r.cost_for_two == 800.0
        assert r.votes == 1200
        assert r.online_order is True
        assert r.book_table is False

    def test_location_is_neighbourhood(self):
        row = _make_row(location="indiranagar")
        r = preprocess_row(row, 0)
        assert r is not None
        assert r.location == "Indiranagar"
        assert r.city == "Bangalore"

    def test_missing_name_returns_none(self):
        row = _make_row(name="")
        assert preprocess_row(row, 0) is None

    def test_none_name_returns_none(self):
        row = _make_row()
        row["name"] = None
        assert preprocess_row(row, 0) is None

    def test_zero_rating_zero_votes_returns_none(self):
        row = _make_row(rating="NEW", votes="0")
        assert preprocess_row(row, 0) is None

    def test_zero_rating_with_votes_kept(self):
        row = _make_row(rating="0", votes="50")
        r = preprocess_row(row, 0)
        assert r is not None
        assert r.rating == 0.0
        assert r.votes == 50


# ═══════════════════════════════════════════════════════════════════════════
# Dataset-level preprocessing
# ═══════════════════════════════════════════════════════════════════════════

class TestPreprocessDataset:
    def test_filters_bad_rows(self):
        rows = [
            _make_row(name="Good", rating="4.0", votes="100"),
            _make_row(name="", rating="4.0", votes="100"),  # bad name
            _make_row(name="Ghost", rating="NEW", votes="0"),  # low quality
            _make_row(name="Also Good", rating="3.5", votes="50"),
        ]
        result = preprocess_dataset(rows)
        assert len(result) == 2
        assert result[0].name == "Good"
        assert result[1].name == "Also Good"

    def test_empty_input(self):
        assert preprocess_dataset([]) == []


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _make_row(
    *,
    name: str = "Test Restaurant",
    location: str = "koramangala",
    url: str = "https://www.zomato.com/bangalore/test-restaurant",
    cuisines: str = "North Indian, Chinese",
    rating: str = "4.2",
    cost: str = "800",
    votes: str = "1200",
    online_order: str = "Yes",
    book_table: str = "No",
    rest_type: str = "Casual Dining",
    dish_liked: str = "Biryani, Pasta",
    address: str = "123 Test St, Koramangala, Bangalore",
) -> dict:
    """Build a synthetic raw row matching the actual Zomato dataset columns.

    Note: The real dataset has no ``city`` column. City is derived from
    ``url`` or ``address``. ``listed_in(city)`` contains neighbourhood
    names, not cities.
    """
    return {
        "name": name,
        "url": url,
        "location": location,
        "cuisines": cuisines,
        "rate": rating,
        "approx_cost(for two people)": cost,
        "votes": votes,
        "online_order": online_order,
        "book_table": book_table,
        "rest_type": rest_type,
        "dish_liked": dish_liked,
        "address": address,
        "listed_in(city)": "Koramangala 5th Block",  # neighbourhood, not city
        "listed_in(type)": "Delivery",
    }
