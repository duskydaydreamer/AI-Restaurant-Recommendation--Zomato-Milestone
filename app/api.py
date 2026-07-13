"""
FastAPI REST API for the Restaurant Recommendation System.

Endpoints:
  - POST /api/recommendations  — get AI-powered recommendations
  - GET  /api/locations         — list all available locations
  - GET  /api/cuisines          — list all available cuisines
  - GET  /api/health            — health check with dataset stats
"""

import logging
import os
import re
import urllib.parse
from contextlib import asynccontextmanager
import concurrent.futures

from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import GROQ_API_KEY, GROQ_MODEL, DATASET_NAME
from app.data.loader import load_restaurants
from app.models.restaurant import Restaurant
from app.models.user_preferences import UserPreferences
from app.services.recommender import get_recommendations

# ── Logging ─────────────────────────────────────────────────────────────────
from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# ── In-memory dataset ──────────────────────────────────────────────────────
_dataset: list[Restaurant] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-load dataset on startup."""
    global _dataset
    logger.info("Loading restaurant dataset on startup…")
    _dataset = load_restaurants()
    logger.info("Dataset ready: %d restaurants", len(_dataset))
    yield
    logger.info("Shutting down.")


# ── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Restaurant Recommender API",
    description="AI-powered restaurant recommendation service using Groq LLM",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the frontend to call the API
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # tightened in production via ALLOWED_ORIGINS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response schemas ──────────────────────────────────────────────

class RecommendationRequest(BaseModel):
    """User preferences for the recommendation engine."""
    location: str = Field(..., min_length=1, description="Neighbourhood / area")
    budget: str = Field(
        default="medium",
        description="Budget tier: 'low', 'medium', or 'high'",
    )
    cuisine: str = Field(default="", description="Preferred cuisine (optional)")
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    additional_preferences: str = Field(
        default="", max_length=500, description="Free-text soft constraints"
    )
    top_k: int = Field(default=5, ge=1, le=10)


class RecommendationItemResponse(BaseModel):
    restaurant_id: str
    rank: int
    name: str
    cuisine: str
    rating: float
    estimated_cost: str
    explanation: str
    location: Optional[str] = None
    image_url: Optional[str] = None
    url: Optional[str] = None


class RecommendationAPIResponse(BaseModel):
    summary: str
    recommendations: list[RecommendationItemResponse]
    relaxations: list[str]
    fallback_used: bool
    candidate_count: int


class LocationsResponse(BaseModel):
    locations: list[str]
    count: int


class CuisinesResponse(BaseModel):
    cuisines: list[str]
    count: int


class HealthResponse(BaseModel):
    status: str
    dataset_name: str
    restaurant_count: int
    location_count: int
    groq_model: str
    groq_key_configured: bool


class ErrorResponse(BaseModel):
    detail: str


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.post(
    "/api/recommendations",
    response_model=RecommendationAPIResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
async def recommend(request: RecommendationRequest):
    """Get AI-powered restaurant recommendations."""
    if request.budget not in ("low", "medium", "high"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid budget '{request.budget}'. Must be 'low', 'medium', or 'high'.",
        )

    prefs = UserPreferences(
        location=request.location,
        budget=request.budget,
        cuisine=request.cuisine,
        min_rating=request.min_rating,
        additional_preferences=request.additional_preferences,
        top_k=request.top_k,
    )

    result = get_recommendations(prefs, _dataset)

    if not result.response or not result.response.recommendations:
        return RecommendationAPIResponse(
            summary="No restaurants found matching your criteria.",
            recommendations=[],
            relaxations=result.relaxations,
            fallback_used=result.fallback_used,
            candidate_count=result.candidate_count,
        )

    recs = []
    for i, r in enumerate(result.response.recommendations):
        # Safely get location and city from the original dataset
        rest_location = ""
        rest_city = ""
        rest_url = ""
        for rest in _dataset:
            if rest.id == r.restaurant_id:
                rest_location = getattr(rest, "location", "")
                rest_city = getattr(rest, "city", "")
                rest_url = getattr(rest, "url", "")
                break
        
        # Clean name (strip chain sub-labels like "Maia - Eat | Bake | Mom")
        clean_name = re.split(r'[-|]', r.name)[0].strip()

        # Build a highly specific query that is unique per restaurant.
        # Including the full original name (r.name) alongside the clean prefix,
        # the location, and the dataset ID ensures Bing resolves a distinct
        # thumbnail for every card — preventing two restaurants from receiving
        # the same cached image.
        query = (
            f'"{clean_name}" {r.name} restaurant {rest_location} {rest_city} '
            f"interior decor food -people -collage -menu "
            f"-site:zomato.com -site:eazydiner.com -site:dineout.co.in -site:magicpin.in"
        )
        query_encoded = urllib.parse.quote(query.strip())

        # &first= offsets the result position — ensures each card in the
        # current response batch fetches from a different index so duplicate
        # thumbnails cannot occur even when queries are semantically similar.
        bing_url = f"https://tse1.mm.bing.net/th?q={query_encoded}&first={i + 1}"
        
        # Format location nicely (e.g., "Brigade Road, Bangalore")
        display_location = r.location
        if rest_location and rest_city and rest_location.lower() != rest_city.lower():
            display_location = f"{rest_location}, {rest_city}"
        elif rest_location or rest_city:
            display_location = rest_location or rest_city

        recs.append(RecommendationItemResponse(
            restaurant_id=r.restaurant_id,
            rank=r.rank,
            name=r.name,
            cuisine=r.cuisine,
            rating=r.rating,
            estimated_cost=r.estimated_cost,
            explanation=r.explanation,
            location=display_location,
            image_url=bing_url,
            url=rest_url
        ))

    return RecommendationAPIResponse(
        summary=result.response.summary,
        recommendations=recs,
        relaxations=result.relaxations,
        fallback_used=result.fallback_used,
        candidate_count=result.candidate_count,
    )


@app.get("/api/locations", response_model=LocationsResponse)
async def get_locations():
    """Return all available locations (neighbourhoods)."""
    locations = sorted({r.location for r in _dataset if r.location})
    return LocationsResponse(locations=locations, count=len(locations))


@app.get("/api/cuisines", response_model=CuisinesResponse)
async def get_cuisines():
    """Return all available cuisines across the dataset."""
    all_cuisines: set[str] = set()
    for r in _dataset:
        for c in r.cuisines:
            if c.strip():
                all_cuisines.add(c.strip().title())
    cuisines = sorted(all_cuisines)
    return CuisinesResponse(cuisines=cuisines, count=len(cuisines))


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    locations = {r.location for r in _dataset if r.location}
    return HealthResponse(
        status="ok" if _dataset else "degraded",
        dataset_name=DATASET_NAME,
        restaurant_count=len(_dataset),
        location_count=len(locations),
        groq_model=GROQ_MODEL,
        groq_key_configured=bool(GROQ_API_KEY),
    )


# ── Serve frontend static files ────────────────────────────────────────────
# Mount AFTER API routes so /api/* takes priority
_frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
