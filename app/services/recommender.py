"""
Recommender orchestrator.

Wires together: filter → prompt → Groq → validate output.

Includes:
  - Input sanitization (architecture §8.4)
  - Structured logging of pipeline stages (implementation-plan §4.1)
  - Post-LLM validation: strip hallucinations, re-merge dataset fields,
    backfill if too many stripped (edge-case §5.3)
  - Fallback to deterministic ranking on Groq failure (§11)
  - Validation failure logging
"""

import logging
import re
import time
from typing import Optional

from app.models.restaurant import Restaurant
from app.models.user_preferences import UserPreferences
from app.models.recommendation import RecommendationResponse, RecommendationItem
from app.services.filter import apply_filters
from app.services.prompt_builder import build_prompt
from app.services.groq_client import get_recommendations_from_llm

logger = logging.getLogger(__name__)


# ── Input sanitization ──────────────────────────────────────────────────────
# Patterns that could be used for prompt injection (architecture §8.4)
_INJECTION_PATTERNS = re.compile(
    r"(ignore previous|forget instructions|system prompt|you are now|"
    r"act as|pretend to be|disregard|override|"
    r"ignore all|reveal your|show me your|what are your instructions|"
    r"bypass|jailbreak)",
    re.IGNORECASE,
)


def sanitize_input(text: str) -> str:
    """Sanitize free-text user input to mitigate prompt injection.

    - Strips leading/trailing whitespace
    - Removes suspicious injection patterns
    - Caps length at 500 characters
    - Logs when sanitization removes content
    """
    if not text:
        return ""
    text = text.strip()
    sanitized = _INJECTION_PATTERNS.sub("[filtered]", text)
    if sanitized != text:
        logger.warning(
            "Prompt injection pattern detected and sanitized in user input"
        )
    return sanitized[:500]


# ── Result container ────────────────────────────────────────────────────────

class RecommenderResult:
    """Container for a recommendation result."""

    def __init__(
        self,
        response: Optional[RecommendationResponse],
        relaxations: list[str],
        fallback_used: bool = False,
        candidate_count: int = 0,
        suggestions: Optional[dict] = None,
    ):
        self.response = response
        self.relaxations = relaxations
        self.fallback_used = fallback_used
        self.candidate_count = candidate_count
        # Suggestions for empty state (nearby cities, popular cuisines)
        self.suggestions = suggestions or {}


# ── Fallback ────────────────────────────────────────────────────────────────

def fallback_recommendation(
    candidates: list[Restaurant], top_k: int
) -> RecommendationResponse:
    """Deterministic fallback when LLM is unavailable.

    Returns the top-K candidates sorted by rating/votes with generic
    explanations (no AI reasoning).
    """
    recs = []
    for i, c in enumerate(candidates[:top_k]):
        recs.append(
            RecommendationItem(
                restaurant_id=c.id,
                rank=i + 1,
                name=c.name,
                cuisine=", ".join(c.cuisines),
                rating=c.rating,
                estimated_cost=f"₹{c.cost_for_two:.0f} for two",
                location=c.location or c.city,
                explanation=(
                    f"{c.name} is a top pick due to its exceptional {c.rating:.1f} rating. It perfectly matches your filters, offering delicious {', '.join(c.cuisines)} at an estimated cost of ₹{c.cost_for_two:.0f} for two."
                ),
            )
        )
    logger.info("Fallback generated %d recommendations (rating-sorted)", len(recs))
    return RecommendationResponse(
        summary="We've analyzed the best dining spots for you. These highly-rated options perfectly match your current filters and budget.",
        recommendations=recs,
    )


# ── Post-LLM validation ────────────────────────────────────────────────────

def _validate_and_merge(
    llm_res: RecommendationResponse,
    candidates: list[Restaurant],
    top_k: int,
) -> RecommendationResponse:
    """Validate LLM output against the candidate set.

    - Strips hallucinated restaurant IDs not in the candidate set
    - Re-merges dataset fields for accuracy (name, rating, cost, cuisines)
    - Re-numbers ranks sequentially
    - Enforces top_k limit
    - Backfills from candidates if too many were stripped (edge-case §5.3)
    """
    valid_ids = {c.id for c in candidates}
    cand_map = {c.id: c for c in candidates}

    valid_recs: list[RecommendationItem] = []
    hallucinated_count = 0

    for rec in llm_res.recommendations:
        if rec.restaurant_id in valid_ids:
            # Re-merge dataset fields for accuracy (never trust LLM for facts)
            c = cand_map[rec.restaurant_id]
            rec.name = c.name
            rec.rating = c.rating
            rec.cuisine = ", ".join(c.cuisines)
            rec.estimated_cost = f"₹{c.cost_for_two:.0f} for two"
            rec.location = c.location or c.city
            valid_recs.append(rec)
        else:
            hallucinated_count += 1
            logger.warning(
                "Stripped hallucinated restaurant_id=%r (name=%r) "
                "not in candidate set",
                rec.restaurant_id,
                rec.name,
            )

    if hallucinated_count:
        logger.warning(
            "Validation: %d/%d LLM recommendations were hallucinated and stripped",
            hallucinated_count,
            len(llm_res.recommendations),
        )

    # ── Backfill if too many stripped (edge-case §5.3) ──────────────────
    used_ids = {r.restaurant_id for r in valid_recs}
    if len(valid_recs) < top_k:
        backfill_count = 0
        for c in candidates:
            if c.id not in used_ids and len(valid_recs) < top_k:
                valid_recs.append(
                    RecommendationItem(
                        restaurant_id=c.id,
                        rank=0,  # will be re-numbered below
                        name=c.name,
                        cuisine=", ".join(c.cuisines),
                        rating=c.rating,
                        estimated_cost=f"₹{c.cost_for_two:.0f} for two",
                        location=c.location or c.city,
                        explanation=(
                            f"This highly-rated ({c.rating:.1f}) spot is a fantastic match for your search, offering excellent {', '.join(c.cuisines)} at ₹{c.cost_for_two:.0f} for two."
                        ),
                    )
                )
                used_ids.add(c.id)
                backfill_count += 1
        if backfill_count:
            logger.info(
                "Backfilled %d recommendations from candidates "
                "(LLM returned insufficient valid results)",
                backfill_count,
            )

    # Enforce top_k and re-number ranks sequentially
    valid_recs = valid_recs[:top_k]
    for i, rec in enumerate(valid_recs):
        rec.rank = i + 1

    # Use the LLM summary if available; fallback to generic
    summary = llm_res.summary if llm_res.summary else (
        "We've analyzed the best dining spots for you. These highly-rated options perfectly match your current preferences."
    )

    return RecommendationResponse(
        summary=summary,
        recommendations=valid_recs,
    )


# ── Main orchestrator ───────────────────────────────────────────────────────

def get_recommendations(
    prefs: UserPreferences, dataset: list[Restaurant]
) -> RecommenderResult:
    """Run the full recommendation pipeline.

    Steps:
      1. Sanitize free-text input
      2. Apply deterministic filters (with progressive relaxation)
      3. Build prompt and call Groq LLM
      4. Validate LLM output (strip hallucinated IDs, re-merge dataset fields)
      5. Fallback to deterministic ranking if LLM fails
    """
    start = time.time()

    # 1. Sanitize
    prefs_clean = prefs.model_copy(
        update={"additional_preferences": sanitize_input(prefs.additional_preferences)}
    )

    logger.info(
        "Pipeline started — location=%r, budget=%s, cuisine=%r, "
        "min_rating=%.1f, top_k=%d",
        prefs_clean.location,
        prefs_clean.budget,
        prefs_clean.cuisine,
        prefs_clean.min_rating,
        prefs_clean.top_k,
    )

    # 2. Filter
    filter_res = apply_filters(dataset, prefs_clean)
    candidates = filter_res.candidates

    logger.info(
        "Filter complete — %d candidates from %d total (relaxations: %s)",
        len(candidates),
        len(dataset),
        filter_res.relaxations or "none",
    )

    if not candidates:
        elapsed = time.time() - start
        logger.warning(
            "No candidates after filtering for %r (%.2fs)",
            prefs_clean.location,
            elapsed,
        )
        return RecommenderResult(
            None,
            filter_res.relaxations,
            candidate_count=0,
            suggestions=filter_res.suggestions,
        )

    # 3. Build prompt & call LLM
    try:
        system_prompt, user_prompt = build_prompt(prefs_clean, candidates)
    except FileNotFoundError:
        logger.error(
            "Prompt template file not found — falling back to deterministic ranking"
        )
        fallback_res = fallback_recommendation(candidates, prefs_clean.top_k)
        elapsed = time.time() - start
        return RecommenderResult(
            fallback_res,
            filter_res.relaxations,
            fallback_used=True,
            candidate_count=len(candidates),
        )

    llm_res = get_recommendations_from_llm(system_prompt, user_prompt)

    if llm_res and llm_res.recommendations:
        # 4. Validate and merge
        validated = _validate_and_merge(llm_res, candidates, prefs_clean.top_k)

        if validated.recommendations:
            elapsed = time.time() - start
            logger.info(
                "Pipeline complete in %.2fs — "
                "%d candidates → %d recommendations (LLM)",
                elapsed,
                len(candidates),
                len(validated.recommendations),
            )
            return RecommenderResult(
                validated,
                filter_res.relaxations,
                fallback_used=False,
                candidate_count=len(candidates),
            )
        else:
            # All LLM results were hallucinated → full fallback
            logger.warning(
                "All LLM recommendations were hallucinated — using full fallback"
            )

    # 5. Fallback
    logger.warning("LLM unavailable or returned no valid results — using deterministic fallback")
    fallback_res = fallback_recommendation(candidates, prefs_clean.top_k)

    elapsed = time.time() - start
    logger.info(
        "Pipeline complete in %.2fs — "
        "%d candidates → %d recommendations (fallback)",
        elapsed,
        len(candidates),
        len(fallback_res.recommendations),
    )
    return RecommenderResult(
        fallback_res,
        filter_res.relaxations,
        fallback_used=True,
        candidate_count=len(candidates),
    )
