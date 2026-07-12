from duckduckgo_search import DDGS
import json

def test():
    with DDGS() as ddgs:
        results = list(ddgs.images("Sante Spa Cuisine Bangalore zomato", max_results=5))
        print(json.dumps(results, indent=2))

test()
