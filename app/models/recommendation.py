from pydantic import BaseModel, Field
from typing import Optional

class RecommendationItem(BaseModel):
    restaurant_id: str = Field(..., description="ID of the recommended restaurant")
    rank: int = Field(..., description="Rank of the recommendation")
    name: str = Field(..., description="Name of the restaurant")
    cuisine: str = Field(..., description="Cuisine of the restaurant")
    rating: float = Field(..., description="Rating of the restaurant")
    estimated_cost: str = Field(..., description="Estimated cost for two")
    location: str = Field(None, description="Location of the restaurant")
    explanation: str = Field(..., description="Explanation for the recommendation")

class RecommendationResponse(BaseModel):
    summary: str = Field(..., description="Summary of the recommendations")
    recommendations: list[RecommendationItem] = Field(..., description="List of recommended restaurants")
