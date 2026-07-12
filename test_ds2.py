from datasets import load_dataset
ds = load_dataset("ManikaSaini/zomato-restaurant-recommendation")
split = ds.get("train") or next(iter(ds.values()))
print(split.features.keys())
print(split[0])
