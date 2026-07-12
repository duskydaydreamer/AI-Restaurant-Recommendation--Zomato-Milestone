import re

with open("app/api.py", "r") as f:
    content = f.read()

old_query = 'query = f"{r.name} restaurant {rest_location} {rest_city} interior empty no people high resolution -collage -people -crowd"'
new_query = 'query = f"{r.name} restaurant {rest_location} {rest_city} interior architecture -people"'

content = content.replace(old_query, new_query)

with open("app/api.py", "w") as f:
    f.write(content)
