"""
Prompt builder.

Constructs the system and user prompts for the Groq LLM from user
preferences and filtered candidates.

Security:
  - User free-text (additional_preferences) is wrapped in delimiters
    and treated as data, not instructions (architecture §8.4)
  - Long fields are truncated to manage token budget (§8.3)

Error handling:
  - Missing prompt template file raises FileNotFoundError (edge-case §4)
"""

import json
import logging
import os
from pathlib import Path

from app.models.restaurant import Restaurant
from app.models.user_preferences import UserPreferences

logger = logging.getLogger(__name__)

# Resolve prompt template path relative to project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_PROMPT_PATH = _PROJECT_ROOT / "prompts" / "recommendation.txt"


def build_prompt(
    prefs: UserPreferences, candidates: list[Restaurant]
) -> tuple[str, str]:
    """Build the system and user prompts for Groq.

    Args:
        prefs: Validated and sanitised user preferences.
        candidates: Pre-filtered restaurant candidates (≤ MAX_CANDIDATES).

    Returns:
        A tuple of ``(system_prompt, user_prompt)``.

    Raises:
        FileNotFoundError: If the prompt template file is missing.
    """
    if not _PROMPT_PATH.exists():
        logger.error("Prompt template not found at %s", _PROMPT_PATH)
        raise FileNotFoundError(
            f"Prompt template not found: {_PROMPT_PATH}. "
            "Ensure prompts/recommendation.txt exists."
        )

    template = _PROMPT_PATH.read_text(encoding="utf-8")

    system_prompt, user_prompt_template = template.split("[User]")
    system_prompt = system_prompt.replace("[System]", "").strip()
    user_prompt_template = user_prompt_template.strip()

    # ── Compact candidates to save tokens (architecture §8.3) ───────────
    compact_candidates = []
    for c in candidates:
        compact_candidates.append({
            "id": c.id,
            "name": c.name[:80],  # truncate long names
            "cuisines": c.cuisines[:5],  # cap cuisine list
            "rating": c.rating,
            "cost_for_two": c.cost_for_two,
            "rest_type": c.rest_type[:50] if c.rest_type else "",
        })

    # ── Build preferences JSON with delimiter-wrapped free text ─────────
    prefs_data = prefs.model_dump()
    # Wrap additional_preferences in delimiters for injection safety
    if prefs_data.get("additional_preferences"):
        prefs_data["additional_preferences"] = (
            f"<<<USER_PREFERENCE>>> "
            f"{prefs_data['additional_preferences']} "
            f"<<<END_USER_PREFERENCE>>>"
        )

    user_prompt = user_prompt_template.replace(
        "{preferences_json}", json.dumps(prefs_data, indent=2)
    ).replace(
        "{candidates_json}", json.dumps(compact_candidates, indent=2)
    ).replace(
        "{top_k}", str(prefs.top_k)
    )

    logger.debug(
        "Prompt built — system: %d chars, user: %d chars, candidates: %d",
        len(system_prompt),
        len(user_prompt),
        len(compact_candidates),
    )

    return system_prompt, user_prompt
