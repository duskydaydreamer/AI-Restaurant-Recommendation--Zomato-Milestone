with open("app/api.py", "r") as f:
    content = f.read()

old_url_line = 'bing_url = f"https://tse1.mm.bing.net/th?q={query_encoded}&w=800&h=600&c=7"'
new_url_line = 'bing_url = f"https://tse1.mm.bing.net/th?q={query_encoded}"'

content = content.replace(old_url_line, new_url_line)

with open("app/api.py", "w") as f:
    f.write(content)
