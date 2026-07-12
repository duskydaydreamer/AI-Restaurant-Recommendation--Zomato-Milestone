from app.api import RecommendationItemResponse

r = RecommendationItemResponse(
    restaurant_id="123",
    rank=1,
    name="Test",
    cuisine="Indian",
    rating=4.5,
    estimated_cost="100",
    explanation="Test",
    location="Test Location",
)
print(r.model_dump())
