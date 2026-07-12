from pydantic import BaseModel, Field

class UserPreferences(BaseModel):
    location: str = Field(..., description="Neighbourhood or city to search in")
    budget: str = Field(..., description="Budget tier: 'low', 'medium', or 'high'")
    cuisine: str = Field(default="", description="Preferred cuisine (optional)")
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Minimum rating (0-5)")
    additional_preferences: str = Field(default="", description="Any other preferences (e.g., family-friendly)")
    top_k: int = Field(default=5, ge=1, le=10, description="Number of recommendations to return")
