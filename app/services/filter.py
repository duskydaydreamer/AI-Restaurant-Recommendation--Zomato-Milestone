"""
Candidate filter pipeline.

Applies deterministic hard-constraint filters in sequence:
  location → rating → budget → cuisine → sort → cap

Includes progressive relaxation (architecture §4.3, edge-case §3.2) and
structured logging of candidate counts at each stage (implementation-plan §4.1).
"""

import logging
from typing import Optional

from app.models.restaurant import Restaurant
from app.models.user_preferences import UserPreferences
from app.config import MAX_CANDIDATES

logger = logging.getLogger(__name__)


class FilterResult:
    """Container for filter pipeline output."""

    def __init__(
        self,
        candidates: list[Restaurant],
        relaxations: list[str],
        suggestions: Optional[dict] = None,
    ):
        self.candidates = candidates
        self.relaxations = relaxations
        # Suggestions for empty-state: nearby cities, popular cuisines
        self.suggestions = suggestions or {}


def apply_filters(
    restaurants: list[Restaurant],
    prefs: UserPreferences,
) -> FilterResult:
    """Filter restaurants based on user preferences with progressive relaxation.

    Logs candidate counts at each filter stage for observability.
    Returns suggestions when zero results remain (edge-case §3.2 → §2.2).
    """
    relaxations: list[str] = []

    logger.info(
        "Filter pipeline started — total dataset: %d, query: location=%r, "
        "budget=%s, cuisine=%r, min_rating=%.1f",
        len(restaurants),
        prefs.location,
        prefs.budget,
        prefs.cuisine,
        prefs.min_rating,
    )

    # ── 1. Location filter (hard constraint — no relaxation) ────────────
    # User might type "Marathahalli, Bangalore", we just use the first part for matching
    raw_query = prefs.location.lower().strip()
    loc_query = raw_query.split(',')[0].strip()
    
    loc_candidates = [
        r for r in restaurants
        if loc_query in r.location.lower() or loc_query in r.city.lower()
    ]
    candidates = loc_candidates.copy()
    logger.info(
        "After location filter (%r): %d candidates", prefs.location, len(candidates)
    )

    if not candidates:
        # Build suggestions: available cities + locations
        available_cities = sorted({r.city for r in restaurants})
        popular_cuisines = _popular_cuisines(restaurants, limit=10)
        logger.warning(
            "Location %r not found in dataset. Available cities: %s",
            prefs.location,
            ", ".join(available_cities[:10]),
        )
        return FilterResult(
            [],
            ["Location not found in dataset"],
            suggestions={
                "available_cities": available_cities,
                "popular_cuisines": popular_cuisines,
            },
        )

    # ── 2. Rating filter ────────────────────────────────────────────────
    def filter_by_rating(cands: list[Restaurant], min_r: float) -> list[Restaurant]:
        return [r for r in cands if r.rating >= min_r]

    # ── 3. Budget filter ────────────────────────────────────────────────
    def filter_by_budget(cands: list[Restaurant], budget: str) -> list[Restaurant]:
        return [r for r in cands if r.budget_tier == budget]

    def filter_by_cuisine(cands: list[Restaurant], cuisine: str) -> list[Restaurant]:
        if not cuisine:
            return cands
        user_cuisines = [c.lower().strip() for c in cuisine.split(",") if c.strip()]
        return [
            r for r in cands
            if any(
                any(uc in rc.lower() for rc in r.cuisines)
                for uc in user_cuisines
            )
        ]

    # ── Apply all filters ───────────────────────────────────────────────
    # Budget is a HARD constraint. Apply it immediately to location candidates.
    loc_budget_candidates = filter_by_budget(candidates, prefs.budget)
    logger.info("After budget filter (%s): %d candidates", prefs.budget, len(loc_budget_candidates))

    if not loc_budget_candidates:
        available_cities = sorted({r.city for r in restaurants})
        popular_cuisines = _popular_cuisines(restaurants, limit=10)
        return FilterResult(
            [],
            [f"No restaurants found in {prefs.location} for the '{prefs.budget}' budget tier."],
            suggestions={
                "available_cities": available_cities,
                "popular_cuisines": popular_cuisines,
            },
        )

    # Now apply relaxable constraints (rating and cuisine)
    c_rated = filter_by_rating(loc_budget_candidates, prefs.min_rating)
    logger.info("After rating filter (≥%.1f): %d candidates", prefs.min_rating, len(c_rated))

    c_cuisine = filter_by_cuisine(c_rated, prefs.cuisine)
    logger.info("After cuisine filter (%r): %d candidates", prefs.cuisine or "(any)", len(c_cuisine))

    candidates = c_cuisine

    # ── Progressive Padding (within hard constraints) ───────────────────
    if len(candidates) < prefs.top_k:
        seen_ids = {c.id for c in candidates}
        
        def pad_from(fallback_list: list[Restaurant]):
            sorted_fallback = sorted(fallback_list, key=lambda r: (r.rating, r.votes), reverse=True)
            for r in sorted_fallback:
                if len(candidates) >= prefs.top_k:
                    break
                if r.id not in seen_ids:
                    candidates.append(r)
                    seen_ids.add(r.id)

        # Pad with Rating matches (relaxing Cuisine)
        if len(candidates) < prefs.top_k:
            prev_len = len(candidates)
            pad_from(c_rated)
            if len(candidates) > prev_len and prefs.cuisine:
                relaxations.append("Cuisine requirement relaxed to find more options")

        # Pad with Location+Budget matches (relaxing Rating AND Cuisine)
        if len(candidates) < prefs.top_k:
            prev_len = len(candidates)
            pad_from(loc_budget_candidates)
            if len(candidates) > prev_len:
                relaxations.append("Rating requirement relaxed to find more options")

    # ── Sort and cap ────────────────────────────────────────────────────
    candidates.sort(key=lambda r: (r.rating, r.votes), reverse=True)
    pre_cap = len(candidates)
    candidates = candidates[:MAX_CANDIDATES]

    if pre_cap > MAX_CANDIDATES:
        logger.info(
            "Capped candidates from %d to %d (MAX_CANDIDATES=%d)",
            pre_cap,
            len(candidates),
            MAX_CANDIDATES,
        )

    logger.info(
        "Filter pipeline complete — %d final candidates, relaxations: %s",
        len(candidates),
        relaxations or "none",
    )

    return FilterResult(candidates, relaxations)


def _popular_cuisines(restaurants: list[Restaurant], limit: int = 10) -> list[str]:
    """Return the most common cuisines across the dataset."""
    counts: dict[str, int] = {}
    for r in restaurants:
        for c in r.cuisines:
            c_title = c.strip().title()
            if c_title:
                counts[c_title] = counts.get(c_title, 0) + 1
    return sorted(counts, key=counts.get, reverse=True)[:limit]  # type: ignore[arg-type]
