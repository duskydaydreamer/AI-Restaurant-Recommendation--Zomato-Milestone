"""
Application configuration.

Loads environment variables from a .env file (if present) and exposes
typed settings used throughout the application. No secrets are hardcoded.

Security: GROQ_API_KEY is loaded from the environment only and is never
logged or serialised. See architecture §13.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env from the project root (two levels up from this file)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=_ENV_PATH)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# ---------------------------------------------------------------------------
# Groq LLM
# ---------------------------------------------------------------------------
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TIMEOUT: int = int(os.getenv("GROQ_TIMEOUT", "30"))
GROQ_MAX_RETRIES: int = int(os.getenv("GROQ_MAX_RETRIES", "1"))

# ---------------------------------------------------------------------------
# Hugging Face dataset
# ---------------------------------------------------------------------------
DATASET_NAME: str = os.getenv(
    "DATASET_NAME", "ManikaSaini/zomato-restaurant-recommendation"
)

# ---------------------------------------------------------------------------
# Recommendation pipeline
# ---------------------------------------------------------------------------
MAX_CANDIDATES: int = int(os.getenv("MAX_CANDIDATES", "30"))
DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "5"))

# ---------------------------------------------------------------------------
# Budget tier thresholds (₹ cost_for_two)
# ---------------------------------------------------------------------------
BUDGET_LOW_MAX: int = int(os.getenv("BUDGET_LOW_MAX", "500"))
BUDGET_MEDIUM_MAX: int = int(os.getenv("BUDGET_MEDIUM_MAX", "1500"))


def get_budget_tier(cost_for_two: float) -> str:
    """Derive a budget tier label from the numeric cost for two.

    Thresholds are driven by BUDGET_LOW_MAX and BUDGET_MEDIUM_MAX env vars.

    Returns:
        One of ``"low"``, ``"medium"``, or ``"high"``.
    """
    if cost_for_two <= BUDGET_LOW_MAX:
        return "low"
    if cost_for_two <= BUDGET_MEDIUM_MAX:
        return "medium"
    return "high"


def validate_config() -> list[str]:
    """Return a list of configuration warnings (empty means all OK).

    This is called at startup to surface misconfigurations early without
    crashing the application outright.
    """
    warnings: list[str] = []

    if not GROQ_API_KEY:
        warnings.append(
            "GROQ_API_KEY is not set. LLM features will be unavailable."
        )

    if BUDGET_LOW_MAX >= BUDGET_MEDIUM_MAX:
        warnings.append(
            f"BUDGET_LOW_MAX ({BUDGET_LOW_MAX}) should be less than "
            f"BUDGET_MEDIUM_MAX ({BUDGET_MEDIUM_MAX})."
        )

    if MAX_CANDIDATES < 1:
        warnings.append("MAX_CANDIDATES must be at least 1.")

    if DEFAULT_TOP_K < 1 or DEFAULT_TOP_K > 10:
        warnings.append("DEFAULT_TOP_K should be between 1 and 10.")

    if GROQ_TIMEOUT < 5:
        warnings.append(
            f"GROQ_TIMEOUT ({GROQ_TIMEOUT}s) is very low; "
            "consider at least 10s for reliable LLM calls."
        )

    return warnings
