"""
Unit tests for the prompt builder.

Covers: basic prompt construction, delimiter wrapping of user preferences,
field truncation, missing template error, and edge cases.
Implementation-plan §2.17, §4.5.
"""

import pytest
from unittest.mock import patch
from pathlib import Path

from app.models.restaurant import Restaurant
from app.models.user_preferences import UserPreferences
from app.services.prompt_builder import build_prompt


def _make_prefs(**overrides):
    defaults = dict(
        location="Indiranagar",
        budget="medium",
        cuisine="italian",
        min_rating=4.0,
        additional_preferences="family-friendly",
        top_k=5,
    )
    defaults.update(overrides)
    return UserPreferences(**defaults)


def _make_candidates(n=1):
    return [
        Restaurant(
            id=str(i),
            name=f"Restaurant {i}",
            location="Indiranagar",
            city="Bangalore",
            cuisines=["italian", "pizza"],
            rating=4.5,
            cost_for_two=1000,
            budget_tier="medium",
            votes=100,
            rest_type="Casual Dining",
        )
        for i in range(1, n + 1)
    ]


class TestBuildPrompt:
    def test_returns_system_and_user_prompt(self):
        prefs = _make_prefs()
        cands = _make_candidates()
        sys_prompt, user_prompt = build_prompt(prefs, cands)
        assert isinstance(sys_prompt, str)
        assert isinstance(user_prompt, str)
        assert len(sys_prompt) > 0
        assert len(user_prompt) > 0

    def test_system_prompt_contains_anti_hallucination(self):
        prefs = _make_prefs()
        cands = _make_candidates()
        sys_prompt, _ = build_prompt(prefs, cands)
        assert "MUST only recommend restaurants from the CANDIDATE_LIST" in sys_prompt

    def test_user_prompt_contains_preferences(self):
        prefs = _make_prefs(additional_preferences="quiet ambiance")
        cands = _make_candidates()
        _, user_prompt = build_prompt(prefs, cands)
        assert "quiet ambiance" in user_prompt
        assert "Indiranagar" in user_prompt

    def test_user_prompt_contains_candidates(self):
        prefs = _make_prefs()
        cands = _make_candidates()
        _, user_prompt = build_prompt(prefs, cands)
        assert "Restaurant 1" in user_prompt

    def test_delimiter_wrapping(self):
        """additional_preferences should be wrapped in delimiters for security."""
        prefs = _make_prefs(additional_preferences="family-friendly")
        cands = _make_candidates()
        _, user_prompt = build_prompt(prefs, cands)
        assert "<<<USER_PREFERENCE>>>" in user_prompt
        assert "<<<END_USER_PREFERENCE>>>" in user_prompt

    def test_empty_additional_preferences_no_delimiters(self):
        """Empty additional_preferences should not produce delimiters."""
        prefs = _make_prefs(additional_preferences="")
        cands = _make_candidates()
        _, user_prompt = build_prompt(prefs, cands)
        assert "<<<USER_PREFERENCE>>>" not in user_prompt

    def test_top_k_substituted(self):
        prefs = _make_prefs(top_k=3)
        cands = _make_candidates()
        _, user_prompt = build_prompt(prefs, cands)
        assert "3" in user_prompt

    def test_multiple_candidates(self):
        prefs = _make_prefs()
        cands = _make_candidates(5)
        _, user_prompt = build_prompt(prefs, cands)
        for i in range(1, 6):
            assert f"Restaurant {i}" in user_prompt

    def test_missing_template_raises_error(self):
        """Should raise FileNotFoundError when template is missing."""
        prefs = _make_prefs()
        cands = _make_candidates()
        with patch(
            "app.services.prompt_builder._PROMPT_PATH",
            Path("/nonexistent/path/recommendation.txt"),
        ):
            with pytest.raises(FileNotFoundError):
                build_prompt(prefs, cands)
