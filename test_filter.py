from app.models.restaurant import Restaurant
from app.models.user_preferences import UserPreferences
from app.services.filter import apply_filters

# Create fake restaurants
restaurants = [
    Restaurant(
        id="1",
        name="Test 1",
        location="BTM",
        city="Bangalore",
        cuisines=["north indian"],
        rating=4.0,
        cost_for_two=400,
        budget_tier="low",
    ),
    Restaurant(
        id="2",
        name="Test 2",
        location="BTM",
        city="Bangalore",
        cuisines=["chinese"],
        rating=3.0,
        cost_for_two=800,
        budget_tier="medium",
    )
]

prefs = UserPreferences(
    location="BTM",
    budget="high",
    cuisine="italian",
    min_rating=4.5,
    top_k=5
)

result = apply_filters(restaurants, prefs)
print("Candidates:", len(result.candidates))
for c in result.candidates:
    print("-", c.name)
