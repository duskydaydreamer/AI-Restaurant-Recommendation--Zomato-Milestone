"""
Groq LLM client.

Handles the Chat Completions call to Groq with structured JSON output,
timeout handling, retry with exponential backoff, and structured logging.

Error scenarios handled (architecture §11, edge-case §5.1–5.2):
  - Missing API key → skip LLM, return None
  - Invalid/revoked key (401) → log + return None
  - Rate limit (429) → retry with backoff → return None
  - Service outage (5xx) → retry → return None
  - Timeout (>30s) → retry → return None
  - Invalid JSON response → retry with stricter instruction → return None
  - Empty response → return None

Security (architecture §13, edge-case §9):
  - API key is NEVER logged
  - Prompt content is NOT logged in production (only at DEBUG level)
"""

import json
import logging
import time
from typing import Optional

from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL, GROQ_TIMEOUT, GROQ_MAX_RETRIES
from app.models.recommendation import RecommendationResponse

logger = logging.getLogger(__name__)


def get_recommendations_from_llm(
    system_prompt: str, user_prompt: str
) -> Optional[RecommendationResponse]:
    """Call Groq Chat Completions and parse the response.

    Returns ``None`` on any failure (missing key, timeout, bad JSON, etc.).
    The caller should fall back to deterministic ranking.

    Implements retry logic:
      - 1 retry on transient failures (timeout, rate limit, 5xx)
      - 1 retry on invalid JSON with stricter instructions
    """
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set — skipping LLM call")
        return None

    # Security: only log prompts at DEBUG level (never in production)
    logger.debug("System prompt length: %d chars", len(system_prompt))
    logger.debug("User prompt length: %d chars", len(user_prompt))

    last_error: Optional[Exception] = None
    max_attempts = 1 + GROQ_MAX_RETRIES  # 1 initial + retries

    for attempt in range(1, max_attempts + 1):
        start_time = time.time()
        try:
            client = Groq(api_key=GROQ_API_KEY, timeout=GROQ_TIMEOUT)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            # On retry after JSON failure, add a nudge for valid JSON
            if attempt > 1 and last_error and isinstance(last_error, json.JSONDecodeError):
                messages.append({
                    "role": "user",
                    "content": (
                        "Your previous response was not valid JSON. "
                        "Please return ONLY valid JSON matching the OUTPUT_SCHEMA, "
                        "with no additional text, markdown fences, or comments."
                    ),
                })
                logger.info("Retry %d: added stricter JSON instruction", attempt)

            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=3500,
            )

            elapsed = time.time() - start_time
            content = response.choices[0].message.content

            # ── Log usage stats ─────────────────────────────────────────
            usage = getattr(response, "usage", None)
            if usage:
                logger.info(
                    "Groq response received — attempt=%d/%d, elapsed=%.2fs, "
                    "model=%s, prompt_tokens=%s, completion_tokens=%s, "
                    "total_tokens=%s",
                    attempt,
                    max_attempts,
                    elapsed,
                    GROQ_MODEL,
                    getattr(usage, "prompt_tokens", "?"),
                    getattr(usage, "completion_tokens", "?"),
                    getattr(usage, "total_tokens", "?"),
                )
            else:
                logger.info(
                    "Groq response received — attempt=%d/%d, elapsed=%.2fs, "
                    "model=%s",
                    attempt,
                    max_attempts,
                    elapsed,
                    GROQ_MODEL,
                )

            # ── Warn on slow responses ──────────────────────────────────
            if elapsed > 5.0:
                logger.warning(
                    "Groq latency %.2fs exceeds 5s threshold", elapsed
                )

            if not content:
                logger.warning("Groq returned empty content (attempt %d)", attempt)
                last_error = ValueError("Empty content")
                continue

            data = json.loads(content)
            result = RecommendationResponse.model_validate(data)

            # Validate basic structure
            if not result.recommendations:
                logger.warning(
                    "Groq returned empty recommendations array (attempt %d)",
                    attempt,
                )
                # Still return — the caller decides whether to fallback
                return result

            logger.info(
                "Successfully parsed %d recommendations from Groq",
                len(result.recommendations),
            )
            return result

        except json.JSONDecodeError as e:
            elapsed = time.time() - start_time
            logger.error(
                "Groq returned invalid JSON — attempt=%d/%d, elapsed=%.2fs: %s",
                attempt,
                max_attempts,
                elapsed,
                e,
            )
            last_error = e
            if attempt < max_attempts:
                _backoff(attempt)
                continue
            return None

        except Exception as e:
            elapsed = time.time() - start_time
            error_str = str(e).lower()

            # Categorise the error for better logging
            if "rate_limit" in error_str or "429" in error_str:
                logger.warning(
                    "Groq rate limited (429) — attempt=%d/%d, elapsed=%.2fs",
                    attempt,
                    max_attempts,
                    elapsed,
                )
            elif "timeout" in error_str or "timed out" in error_str:
                logger.warning(
                    "Groq request timed out — attempt=%d/%d, elapsed=%.2fs",
                    attempt,
                    max_attempts,
                    elapsed,
                )
            elif "401" in error_str or "unauthorized" in error_str:
                # Do NOT retry auth failures
                logger.error(
                    "Groq authentication failed (invalid/revoked API key) — "
                    "elapsed=%.2fs. Check GROQ_API_KEY.",
                    elapsed,
                )
                return None
            elif "model" in error_str and "not found" in error_str:
                logger.error(
                    "Groq model %r not found — elapsed=%.2fs. "
                    "Check GROQ_MODEL in .env.",
                    GROQ_MODEL,
                    elapsed,
                )
                return None
            else:
                logger.error(
                    "Groq API call failed — attempt=%d/%d, elapsed=%.2fs: %s",
                    attempt,
                    max_attempts,
                    elapsed,
                    e,
                )

            last_error = e
            if attempt < max_attempts:
                _backoff(attempt)
                continue
            return None

    logger.error(
        "All %d Groq attempts exhausted. Last error: %s",
        max_attempts,
        last_error,
    )
    return None


def _backoff(attempt: int) -> None:
    """Exponential backoff between retries."""
    delay = min(2 ** attempt, 8)  # 2s, 4s, 8s max
    logger.info("Retrying in %ds (attempt %d)…", delay, attempt)
    time.sleep(delay)
