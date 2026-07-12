with open("app/api.py", "r") as f:
    content = f.read()

old_block = """    recs = []
    import urllib.parse
    for i, r in enumerate(result.response.recommendations):
        # Safely get location and city from the original dataset
        rest_location = ""
        rest_city = ""
        for rest in _dataset:
            if rest.id == r.restaurant_id:
                rest_location = getattr(rest, "location", "")
                rest_city = getattr(rest, "city", "")
                break
        
        query = f"{r.name} {rest_location} {rest_city} restaurant photo"
        query_encoded = urllib.parse.quote(query.strip())
        bing_url = f"https://tse1.mm.bing.net/th?q={query_encoded}"
        
        recs.append(RecommendationItemResponse(
            restaurant_id=r.restaurant_id,
            rank=r.rank,
            name=r.name,
            cuisine=r.cuisine,
            rating=r.rating,
            estimated_cost=r.estimated_cost,
            explanation=r.explanation,
            image_url=bing_url
        ))"""

new_block = """    recs = []
    for i, r in enumerate(result.response.recommendations):
        recs.append(RecommendationItemResponse(
            restaurant_id=r.restaurant_id,
            rank=r.rank,
            name=r.name,
            cuisine=r.cuisine,
            rating=r.rating,
            estimated_cost=r.estimated_cost,
            explanation=r.explanation,
            image_url=None
        ))"""

content = content.replace(old_block, new_block)

with open("app/api.py", "w") as f:
    f.write(content)
