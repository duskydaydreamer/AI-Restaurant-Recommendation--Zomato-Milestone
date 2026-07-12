"""
Hugging Face dataset loader.

Fetches the Zomato restaurant dataset from Hugging Face, converts it
to a list of dicts, and passes through the preprocessor.

Features:
  - 3× retry on download failure (implementation-plan §1.6)
  - Logs record count and available cities on success
  - Returns an in-memory ``list[Restaurant]`` for filtering (§1.5)
"""

from __future__ import annotations

import logging
import time
from typing import Any

from datasets import load_dataset  # type: ignore[import-untyped]

from app.config import DATASET_NAME
from app.data.preprocessor import preprocess_dataset
from app.models.restaurant import Restaurant

logger = logging.getLogger(__name__)

# ── Configuration ───────────────────────────────────────────────────────────
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2  # doubles on each retry (exponential backoff)


def _fetch_raw_rows() -> list[dict[str, Any]]:
    """Download the dataset from Hugging Face with retry logic.

    Raises:
        RuntimeError: If all retries are exhausted.
    """
    last_error: Exception | None = None
    delay = RETRY_DELAY_SECONDS

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(
                "Loading dataset '%s' (attempt %d/%d)…",
                DATASET_NAME,
                attempt,
                MAX_RETRIES,
            )
            ds = load_dataset(DATASET_NAME)

            # The dataset may have multiple splits; prefer "train"
            if isinstance(ds, dict):
                split = ds.get("train") or next(iter(ds.values()))
            else:
                split = ds

            rows: list[dict[str, Any]] = [dict(row) for row in split]  # type: ignore[arg-type]
            logger.info(
                "Dataset loaded successfully: %d raw rows", len(rows)
            )

            # Log available column names once for debugging / schema checks
            if rows:
                logger.info("Dataset columns: %s", list(rows[0].keys()))

            return rows

        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warning(
                "Dataset download failed (attempt %d/%d): %s",
                attempt,
                MAX_RETRIES,
                exc,
            )
            if attempt < MAX_RETRIES:
                logger.info("Retrying in %ds…", delay)
                time.sleep(delay)
                delay *= 2  # exponential backoff

    raise RuntimeError(
        f"Failed to load dataset '{DATASET_NAME}' after {MAX_RETRIES} attempts. "
        f"Last error: {last_error}"
    )


# ── In-memory cache ────────────────────────────────────────────────────────
_cached_restaurants: list[Restaurant] | None = None


def load_restaurants(force_reload: bool = False) -> list[Restaurant]:
    """Return the preprocessed restaurant list, loading once and caching.

    Args:
        force_reload: If ``True``, re-download and reprocess the dataset
            even if a cached copy exists.

    Returns:
        A list of validated ``Restaurant`` objects.

    Raises:
        RuntimeError: If the dataset cannot be downloaded after retries.
    """
    global _cached_restaurants  # noqa: PLW0603

    if _cached_restaurants is not None and not force_reload:
        logger.debug(
            "Returning cached dataset (%d records)", len(_cached_restaurants)
        )
        return _cached_restaurants

    load_start = time.time()
    raw_rows = _fetch_raw_rows()
    _cached_restaurants = preprocess_dataset(raw_rows)

    # Guard: empty dataset is a startup failure (edge-case §1.1)
    if not _cached_restaurants:
        raise RuntimeError(
            f"Dataset '{DATASET_NAME}' loaded but produced 0 valid records "
            "after preprocessing. Check dataset schema and preprocessor."
        )

    load_elapsed = time.time() - load_start

    # Final summary
    cities = sorted({r.city for r in _cached_restaurants})
    logger.info(
        "Dataset ready: %d restaurants across %d cities (loaded in %.2fs)",
        len(_cached_restaurants),
        len(cities),
        load_elapsed,
    )
    for city in cities[:10]:
        count = sum(1 for r in _cached_restaurants if r.city == city)
        logger.info("  • %s: %d restaurants", city, count)
    if len(cities) > 10:
        logger.info("  … and %d more cities", len(cities) - 10)

    return _cached_restaurants


def get_available_cities(restaurants: list[Restaurant] | None = None) -> list[str]:
    """Return a sorted list of unique cities in the dataset."""
    if restaurants is None:
        restaurants = load_restaurants()
    return sorted({r.city for r in restaurants})
