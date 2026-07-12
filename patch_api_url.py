import re

with open("app/api.py", "r") as f:
    content = f.read()

# Add url to response model
content = content.replace("    image_url: Optional[str] = None\n", "    image_url: Optional[str] = None\n    url: Optional[str] = None\n")

# Extract url in loop
old_extract = """        for rest in _dataset:
            if rest.id == r.restaurant_id:
                rest_location = getattr(rest, "location", "")
                rest_city = getattr(rest, "city", "")
                break"""
new_extract = """        rest_url = ""
        for rest in _dataset:
            if rest.id == r.restaurant_id:
                rest_location = getattr(rest, "location", "")
                rest_city = getattr(rest, "city", "")
                rest_url = getattr(rest, "url", "")
                break"""
content = content.replace(old_extract, new_extract)

# Add url to RecommendationItemResponse
old_append = """            explanation=r.explanation,
            image_url=bing_url
        ))"""
new_append = """            explanation=r.explanation,
            image_url=bing_url,
            url=rest_url
        ))"""
content = content.replace(old_append, new_append)

with open("app/api.py", "w") as f:
    f.write(content)
