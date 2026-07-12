from datasets import load_dataset
ds = load_dataset("shrutisaxena/zomato-restaurant-data")
split = ds.get("train") or next(iter(ds.values()))
print(split.features.keys())
print(split[0])
