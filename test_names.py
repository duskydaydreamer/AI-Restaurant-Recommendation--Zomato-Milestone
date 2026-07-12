import sys
import os
sys.path.append(os.getcwd())
from app.data.loader import load_restaurants

dataset = load_restaurants()
print("Top 20 restaurant names:")
for i, r in enumerate(dataset[:20]):
    print(f"{i+1}: {r.name}")
