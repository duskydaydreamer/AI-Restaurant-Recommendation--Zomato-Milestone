"""
Restaurant data model.

Canonical internal schema for a restaurant record, derived from the
Hugging Face Zomato dataset after preprocessing.

See: architecture.md §4.1 — Canonical restaurant record
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Restaurant(BaseModel):
    """A preprocessed restaurant record ready for filtering and display."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(
        ..., description="Unique identifier (row index or dataset-provided)"
    )
    name: str = Field(..., description="Restaurant name")
    location: str = Field(
        ..., description="Neighbourhood / area within the city"
    )
    city: str = Field(..., description="City (normalised)")
    cuisines: list[str] = Field(
        default_factory=list,
        description="List of cuisines offered (normalised, deduplicated)",
    )
    rating: float = Field(
        default=0.0, ge=0.0, le=5.0, description="Aggregate rating (0–5)"
    )
    cost_for_two: float = Field(
        default=0.0, ge=0.0, description="Approximate cost for two (₹)"
    )
    budget_tier: str = Field(
        default="low",
        description="Derived tier: 'low', 'medium', or 'high'",
    )
    address: str = Field(default="", description="Full address if available")
    url: str = Field(default="", description="Zomato URL")
    votes: int = Field(default=0, ge=0, description="Number of user votes")
    online_order: bool = Field(
        default=False, description="Whether online ordering is available"
    )
    book_table: bool = Field(
        default=False, description="Whether table booking is available"
    )
    rest_type: str = Field(
        default="", description="Restaurant type (e.g. Casual Dining, Café)"
    )
    dish_liked: list[str] = Field(
        default_factory=list, description="Popular / liked dishes"
    )

