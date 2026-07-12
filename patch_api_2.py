import re

with open("app/api.py", "r") as f:
    content = f.read()

api_ret_old = """    image_urls = []
    def fetch_img(r):
        return fetch_restaurant_image_url(r.name, getattr(r, "location", "") or "", "Bangalore")"""

api_ret_new = """    image_urls = []
    def fetch_img(r):
        # find the restaurant in _dataset by id
        for rest in _dataset:
            if rest.id == r.restaurant_id:
                return fetch_restaurant_image_url(getattr(rest, "url", ""))
        return "" """

content = content.replace(api_ret_old, api_ret_new)

with open("app/api.py", "w") as f:
    f.write(content)
