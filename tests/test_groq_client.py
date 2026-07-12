"""
Unit tests for the Groq client.

Covers: missing API key, successful call, JSON parse error with retry,
timeout, rate limit, auth failure, and empty response.
Implementation-plan §2.17, §4.5.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from app.services.groq_client import get_recommendations_from_llm


# ═══════════════════════════════════════════════════════════════════════════
# Missing API key
# ═══════════════════════════════════════════════════════════════════════════

class TestMissingApiKey:
    @patch("app.services.groq_client.GROQ_API_KEY", "")
    def test_returns_none_when_no_key(self):
        result = get_recommendations_from_llm("system", "user")
        assert result is None


# ═══════════════════════════════════════════════════════════════════════════
# Successful call
# ═══════════════════════════════════════════════════════════════════════════

class TestSuccessfulCall:
    @patch("app.services.groq_client.GROQ_API_KEY", "test-key")
    @patch("app.services.groq_client.Groq")
    def test_valid_response_parsed(self, MockGroq):
        mock_client = MockGroq.return_value
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "summary": "Great options!",
            "recommendations": [
                {
                    "restaurant_id": "1",
                    "rank": 1,
                    "name": "Test Restaurant",
                    "cuisine": "Italian",
                    "rating": 4.5,
                    "estimated_cost": "₹1000 for two",
                    "explanation": "Excellent Italian food."
                }
            ]
        })
        mock_response.usage = MagicMock(
            prompt_tokens=100, completion_tokens=200, total_tokens=300
        )
        mock_client.chat.completions.create.return_value = mock_response

        result = get_recommendations_from_llm("system prompt", "user prompt")
        assert result is not None
        assert result.summary == "Great options!"
        assert len(result.recommendations) == 1
        assert result.recommendations[0].restaurant_id == "1"


# ═══════════════════════════════════════════════════════════════════════════
# Error handling
# ═══════════════════════════════════════════════════════════════════════════

class TestErrorHandling:
    @patch("app.services.groq_client.GROQ_API_KEY", "test-key")
    @patch("app.services.groq_client.GROQ_MAX_RETRIES", 0)
    @patch("app.services.groq_client.Groq")
    def test_timeout_returns_none(self, MockGroq):
        mock_client = MockGroq.return_value
        mock_client.chat.completions.create.side_effect = Exception(
            "Request timed out"
        )
        result = get_recommendations_from_llm("system", "user")
        assert result is None

    @patch("app.services.groq_client.GROQ_API_KEY", "test-key")
    @patch("app.services.groq_client.GROQ_MAX_RETRIES", 0)
    @patch("app.services.groq_client.Groq")
    def test_rate_limit_returns_none(self, MockGroq):
        mock_client = MockGroq.return_value
        mock_client.chat.completions.create.side_effect = Exception(
            "rate_limit_exceeded 429"
        )
        result = get_recommendations_from_llm("system", "user")
        assert result is None

    @patch("app.services.groq_client.GROQ_API_KEY", "test-key")
    @patch("app.services.groq_client.GROQ_MAX_RETRIES", 0)
    @patch("app.services.groq_client.Groq")
    def test_auth_failure_returns_none(self, MockGroq):
        mock_client = MockGroq.return_value
        mock_client.chat.completions.create.side_effect = Exception(
            "401 Unauthorized"
        )
        result = get_recommendations_from_llm("system", "user")
        assert result is None

    @patch("app.services.groq_client.GROQ_API_KEY", "test-key")
    @patch("app.services.groq_client.GROQ_MAX_RETRIES", 0)
    @patch("app.services.groq_client.Groq")
    def test_empty_content_returns_none(self, MockGroq):
        mock_client = MockGroq.return_value
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ""
        mock_response.usage = None
        mock_client.chat.completions.create.return_value = mock_response

        result = get_recommendations_from_llm("system", "user")
        assert result is None

    @patch("app.services.groq_client.GROQ_API_KEY", "test-key")
    @patch("app.services.groq_client.GROQ_MAX_RETRIES", 0)
    @patch("app.services.groq_client.Groq")
    def test_invalid_json_returns_none(self, MockGroq):
        mock_client = MockGroq.return_value
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "not json at all"
        mock_response.usage = None
        mock_client.chat.completions.create.return_value = mock_response

        result = get_recommendations_from_llm("system", "user")
        assert result is None

    @patch("app.services.groq_client.GROQ_API_KEY", "test-key")
    @patch("app.services.groq_client.GROQ_MAX_RETRIES", 0)
    @patch("app.services.groq_client.Groq")
    def test_model_not_found_returns_none(self, MockGroq):
        mock_client = MockGroq.return_value
        mock_client.chat.completions.create.side_effect = Exception(
            "model not found: invalid-model"
        )
        result = get_recommendations_from_llm("system", "user")
        assert result is None


# ═══════════════════════════════════════════════════════════════════════════
# Retry logic
# ═══════════════════════════════════════════════════════════════════════════

class TestRetryLogic:
    @patch("app.services.groq_client._backoff")
    @patch("app.services.groq_client.GROQ_API_KEY", "test-key")
    @patch("app.services.groq_client.GROQ_MAX_RETRIES", 1)
    @patch("app.services.groq_client.Groq")
    def test_retry_on_transient_failure(self, MockGroq, mock_backoff):
        """First call fails, retry succeeds."""
        mock_client = MockGroq.return_value

        success_response = MagicMock()
        success_response.choices = [MagicMock()]
        success_response.choices[0].message.content = json.dumps({
            "summary": "Retried!",
            "recommendations": [
                {
                    "restaurant_id": "1", "rank": 1, "name": "R1",
                    "cuisine": "Italian", "rating": 4.5,
                    "estimated_cost": "₹1000", "explanation": "Good",
                }
            ]
        })
        success_response.usage = None

        mock_client.chat.completions.create.side_effect = [
            Exception("timeout"),
            success_response,
        ]

        result = get_recommendations_from_llm("system", "user")
        assert result is not None
        assert result.summary == "Retried!"
        mock_backoff.assert_called_once()
