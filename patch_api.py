import re

with open("app/api.py", "r") as f:
    content = f.read()

# Add imports
imports = """from contextlib import asynccontextmanager
import concurrent.futures
from app.services.image_fetcher import fetch_restaurant_image_url
"""
content = content.replace("from contextlib import asynccontextmanager", imports)

# Update RecommendationItemResponse
item_resp_old = """class RecommendationItemResponse(BaseModel):
    restaurant_id: str
    rank: int
    name: str
    cuisine: str
    rating: float
    estimated_cost: str
    explanation: str"""

item_resp_new = """class RecommendationItemResponse(BaseModel):
    restaurant_id: str
    rank: int
    name: str
    cuisine: str
    rating: float
    estimated_cost: str
    explanation: str
    image_url: Optional[str] = None"""

content = content.replace(item_resp_old, item_resp_new)

# Update recommend logic
api_ret_old = """    return RecommendationAPIResponse(
        summary=result.response.summary,
        recommendations=[
            RecommendationItemResponse(
                restaurant_id=r.restaurant_id,
                rank=r.rank,
                name=r.name,
                cuisine=r.cuisine,
                rating=r.rating,
                estimated_cost=r.estimated_cost,
                explanation=r.explanation,
            )
            for r in result.response.recommendations
        ],
        relaxations=result.relaxations,
        fallback_used=result.fallback_used,
        candidate_count=result.candidate_count,
    )"""

api_ret_new = """    image_urls = []
    def fetch_img(r):
        return fetch_restaurant_image_url(r.name, getattr(r, "location", "") or "", "Bangalore")

    if result.response and result.response.recommendations:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            image_urls = list(executor.map(fetch_img, result.response.recommendations))

    recs = []
    for i, r in enumerate(result.response.recommendations):
        recs.append(RecommendationItemResponse(
            restaurant_id=r.restaurant_id,
            rank=r.rank,
            name=r.name,
            cuisine=r.cuisine,
            rating=r.rating,
            estimated_cost=r.estimated_cost,
            explanation=r.explanation,
            image_url=image_urls[i] if i < len(image_urls) else None
        ))

    return RecommendationAPIResponse(
        summary=result.response.summary,
        recommendations=recs,
        relaxations=result.relaxations,
        fallback_used=result.fallback_used,
        candidate_count=result.candidate_count,
    )"""

content = content.replace(api_ret_old, api_ret_new)

with open("app/api.py", "w") as f:
    f.write(content)
