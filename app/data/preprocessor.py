"""
Dataset preprocessor.

Transforms raw Hugging Face rows into validated ``Restaurant`` instances.

Preprocessing rules (architecture §4.1, implementation-plan §1.4):
  - Normalise city / location casing & aliases
  - Split, lowercase, and deduplicate cuisines
  - Parse ``cost_for_two`` from potentially messy strings
  - Derive ``budget_tier`` from configurable thresholds
  - Coerce rating to float; flag low-quality records
  - Parse boolean fields (online_order, book_table)
  - Split dish_liked
"""

from __future__ import annotations

import logging
import re
from typing import Any

from app.config import get_budget_tier
from app.models.restaurant import Restaurant

logger = logging.getLogger(__name__)

# ── City alias map ──────────────────────────────────────────────────────────
# Keys are lowercased variants; values are the canonical city name.
CITY_ALIASES: dict[str, str] = {
    "bengaluru": "Bangalore",
    "bangalore": "Bangalore",
    "new delhi": "New Delhi",
    "delhi": "New Delhi",
    "ncr": "New Delhi",
    "mumbai": "Mumbai",
    "bombay": "Mumbai",
    "chennai": "Chennai",
    "madras": "Chennai",
    "kolkata": "Kolkata",
    "calcutta": "Kolkata",
    "hyderabad": "Hyderabad",
    "pune": "Pune",
    "jaipur": "Jaipur",
    "lucknow": "Lucknow",
    "chandigarh": "Chandigarh",
    "ahmedabad": "Ahmedabad",
    "goa": "Goa",
    "kochi": "Kochi",
    "indore": "Indore",
}


# ── Helper utilities ────────────────────────────────────────────────────────

def normalise_city(raw: Any) -> str:
    """Return a canonical city name, title-cased at minimum."""
    if not raw or not isinstance(raw, str):
        return "Unknown"
    cleaned = raw.strip()
    canonical = CITY_ALIASES.get(cleaned.lower())
    if canonical:
        return canonical
    # Fallback: title-case the original value
    return cleaned.title()


def normalise_location(raw: Any) -> str:
    """Strip and title-case a neighbourhood / area string."""
    if not raw or not isinstance(raw, str):
        return "Unknown"
    val = raw.strip().title()
    # Fix ordinals caused by .title() (e.g., 1St -> 1st, 2Nd -> 2nd)
    import re
    val = re.sub(r'(\d)(St|Nd|Rd|Th)\b', lambda m: m.group(1) + m.group(2).lower(), val)
    return val


def parse_cuisines(raw: Any) -> list[str]:
    """Split a comma-separated cuisine string into a deduplicated list.

    Example:
        ``"North Indian, Chinese, North Indian"`` → ``["north indian", "chinese"]``
    """
    if not raw or not isinstance(raw, str):
        return []
    seen: set[str] = set()
    result: list[str] = []
    for c in raw.split(","):
        c = c.strip().lower()
        if c and c not in seen:
            seen.add(c)
            result.append(c)
    return result


def parse_cost(raw: Any) -> float:
    """Extract a numeric cost-for-two value from potentially messy input.

    Handles strings like ``"800"``, ``"₹ 1,200"``, ``"1200.0"``, etc.
    Returns 0.0 on failure.
    """
    if isinstance(raw, (int, float)):
        return max(0.0, float(raw))
    if not isinstance(raw, str):
        return 0.0
    # Remove currency symbols, commas, whitespace
    cleaned = re.sub(r"[₹,$\s,]", "", raw)
    try:
        return max(0.0, float(cleaned))
    except (ValueError, TypeError):
        return 0.0


def parse_rating(raw: Any) -> float:
    """Coerce a rating value to a float in [0, 5].

    Handles strings like ``"4.1/5"``, ``"4.1"``, ``"NEW"``, ``"-"``, etc.
    Returns 0.0 on failure.
    """
    if isinstance(raw, (int, float)):
        val = float(raw)
        return max(0.0, min(val, 5.0))
    if not isinstance(raw, str):
        return 0.0
    cleaned = raw.strip()
    # Handle "4.1/5" format
    if "/" in cleaned:
        cleaned = cleaned.split("/")[0].strip()
    # Handle textual placeholders
    if cleaned.lower() in ("new", "-", "", "nan", "none", "--"):
        return 0.0
    try:
        val = float(cleaned)
        return max(0.0, min(val, 5.0))
    except (ValueError, TypeError):
        return 0.0


def parse_bool_field(raw: Any) -> bool:
    """Parse a boolean-ish field (``"Yes"`` / ``"No"`` or actual bools)."""
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, (int, float)):
        return bool(raw)
    if isinstance(raw, str):
        return raw.strip().lower() in ("yes", "true", "1")
    return False


def parse_dish_liked(raw: Any) -> list[str]:
    """Split a comma-separated dish string into a list."""
    if not raw or not isinstance(raw, str):
        return []
    return [d.strip() for d in raw.split(",") if d.strip()]


def parse_votes(raw: Any) -> int:
    """Coerce a vote count to a non-negative integer."""
    if isinstance(raw, int):
        return max(0, raw)
    if isinstance(raw, float):
        return max(0, int(raw))
    if isinstance(raw, str):
        cleaned = re.sub(r"[,\s]", "", raw.strip())
        try:
            return max(0, int(float(cleaned)))
        except (ValueError, TypeError):
            return 0
    return 0


# ── Column-name mapping ────────────────────────────────────────────────────
# The Zomato dataset column names are inconsistent across versions.
# We try several possible names for each field and take the first match.
#
# NOTE: The Zomato Bangalore dataset has NO explicit "city" column.
# ``listed_in(city)`` actually contains neighbourhood/area names (e.g.
# "Indiranagar", "BTM"), NOT the city.  We extract the real city from
# the ``address`` or ``url`` fields instead.

_COLUMN_MAP: dict[str, list[str]] = {
    "name": ["name", "restaurant_name", "Restaurant Name"],
    "location": ["location", "locality", "area", "Location"],
    "city": ["city", "City"],  # only match an actual city column
    "cuisines": ["cuisines", "cuisine", "Cuisines"],
    "rating": ["rate", "rating", "aggregate_rating", "Rating"],
    "cost_for_two": [
        "approx_cost(for two people)",
        "cost_for_two",
        "average_cost_for_two",
        "cost",
        "Cost",
    ],
    "votes": ["votes", "Votes"],
    "online_order": ["online_order", "has_online_delivery", "Online Order"],
    "book_table": ["book_table", "has_table_booking", "Book Table"],
    "rest_type": ["rest_type", "restaurant_type", "type", "listed_in(type)"],
    "dish_liked": ["dish_liked", "dishes_liked", "Dish Liked"],
    "address": ["address", "Address"],
    "url": ["url", "URL"],
}


def extract_city_from_row(row: dict[str, Any]) -> str:
    """Derive the city name from the row, since the dataset may lack a
    dedicated city column.

    Strategy:
      1. If an explicit ``city`` column exists, use it.
      2. Try to extract from the ``url`` (e.g. zomato.com/bangalore/...).
      3. Try to extract from the ``address`` tail.
      4. Fallback to ``"Bangalore"`` (the dataset is Bangalore-only).
    """
    # 1. Explicit city column
    explicit = _resolve_column(row, "city")
    if explicit and isinstance(explicit, str) and explicit.strip():
        return normalise_city(explicit)

    # 2. Extract from URL: https://www.zomato.com/bangalore/...
    url = _resolve_column(row, "url")
    if url and isinstance(url, str):
        match = re.search(r"zomato\.com/([a-zA-Z-]+)/", url)
        if match:
            city_slug = match.group(1).replace("-", " ")
            return normalise_city(city_slug)

    # 3. Extract from address — look for known city names
    address = _resolve_column(row, "address")
    if address and isinstance(address, str):
        addr_lower = address.lower()
        for alias, canonical in CITY_ALIASES.items():
            if alias in addr_lower:
                return canonical

    # 4. Fallback for this dataset
    return "Bangalore"


def _resolve_column(row: dict[str, Any], field: str) -> Any:
    """Return the value for *field* by trying known column-name variants."""
    for col_name in _COLUMN_MAP.get(field, []):
        if col_name in row:
            return row[col_name]
    return None


# ── Main preprocessing function ────────────────────────────────────────────

def preprocess_row(row: dict[str, Any], row_index: int) -> Restaurant | None:
    """Convert a single raw dataset row into a ``Restaurant``, or ``None``
    if the record is too low-quality to keep.

    Low-quality criteria:
      - Missing or empty name
      - Rating == 0 AND votes == 0 (no signal at all)
    """
    name = _resolve_column(row, "name")
    if not name or (isinstance(name, str) and not name.strip()):
        logger.debug("Skipping row %d: missing name", row_index)
        return None
    
    name = str(name).strip()
    # Fix repeated mojibake in "Santé Spa Cuisine"
    if name.startswith("Sant") and "Spa Cuisine" in name:
        name = "Santé Spa Cuisine"

    rating = parse_rating(_resolve_column(row, "rating"))
    votes = parse_votes(_resolve_column(row, "votes"))

    # Flag low-quality: no rating AND no votes
    if rating == 0.0 and votes == 0:
        logger.debug(
            "Skipping row %d (%s): zero rating and zero votes",
            row_index,
            name,
        )
        return None

    cost = parse_cost(_resolve_column(row, "cost_for_two"))
    city = extract_city_from_row(row)
    location = normalise_location(_resolve_column(row, "location"))

    return Restaurant(
        id=str(row_index),
        name=name,
        location=location,
        city=city,
        cuisines=parse_cuisines(_resolve_column(row, "cuisines")),
        rating=rating,
        cost_for_two=cost,
        budget_tier=get_budget_tier(cost),
        address=str(_resolve_column(row, "address") or ""),
        url=str(_resolve_column(row, "url") or ""),
        votes=votes,
        online_order=parse_bool_field(_resolve_column(row, "online_order")),
        book_table=parse_bool_field(_resolve_column(row, "book_table")),
        rest_type=str(_resolve_column(row, "rest_type") or "").strip(),
        dish_liked=parse_dish_liked(_resolve_column(row, "dish_liked")),
    )


def _deduplicate(restaurants: list[Restaurant]) -> list[Restaurant]:
    """Remove duplicate restaurants (same name + location).

    The Zomato dataset often has the same restaurant listed multiple times
    under different ``listed_in(type)`` values (e.g., Delivery vs Dine-out).
    We keep the entry with the highest vote count.
    """
    best: dict[str, Restaurant] = {}
    for r in restaurants:
        key = (r.name.lower().strip(), r.location.lower().strip())
        key_str = f"{key[0]}|{key[1]}"
        existing = best.get(key_str)
        if existing is None or r.votes > existing.votes:
            best[key_str] = r
        elif r.votes == existing.votes and r.cost_for_two > existing.cost_for_two:
            best[key_str] = r

    deduped = list(best.values())
    removed = len(restaurants) - len(deduped)
    if removed:
        logger.info("Deduplication removed %d duplicate entries", removed)
    return deduped


def preprocess_dataset(rows: list[dict[str, Any]]) -> list[Restaurant]:
    """Preprocess an entire list of raw rows into ``Restaurant`` objects.

    Skips low-quality records, deduplicates, and logs summary statistics.
    """
    restaurants: list[Restaurant] = []
    skipped = 0

    for idx, row in enumerate(rows):
        r = preprocess_row(row, idx)
        if r is not None:
            restaurants.append(r)
        else:
            skipped += 1

    # Deduplicate
    restaurants = _deduplicate(restaurants)

    # ── Summary logging ─────────────────────────────────────────────────
    cities = sorted({r.city for r in restaurants})
    locations = sorted({r.location for r in restaurants})
    logger.info(
        "Preprocessing complete: %d records kept, %d skipped",
        len(restaurants),
        skipped,
    )
    logger.info("Available cities (%d): %s", len(cities), ", ".join(cities))
    logger.info(
        "Available locations (%d): %s",
        len(locations),
        ", ".join(locations[:20]) + ("…" if len(locations) > 20 else ""),
    )

    return restaurants

