import re
import urllib.parse

with open("app/api.py", "r") as f:
    content = f.read()

# Replace the fetch_img block
api_ret_old = """    image_urls = []
    def fetch_img(r):
        # find the restaurant in _dataset by id
        for rest in _dataset:
            if rest.id == r.restaurant_id:
                return fetch_restaurant_image_url(getattr(rest, "url", ""))
        return "" 

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
        ))"""

api_ret_new = """    recs = []
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

content = content.replace(api_ret_old, api_ret_new)

with open("app/api.py", "w") as f:
    f.write(content)
