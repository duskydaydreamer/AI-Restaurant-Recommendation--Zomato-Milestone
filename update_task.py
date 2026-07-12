import re

with open("/Users/bhawna/.gemini/antigravity-ide/brain/1112063e-d36f-414a-9c86-9a578decd29e/task.md", "r") as f:
    content = f.read()

content = content.replace("- `[ ]` Update `app/api.py` to include refined Bing image search logic.", "- `[x]` Update `app/api.py` to include refined Bing image search logic.")
content = content.replace("  - `[ ]` Use the refined search query", "  - `[x]` Use the refined search query")
content = content.replace("  - `[ ]` Append `&w=800&h=600&c=7`", "  - `[x]` Append `&w=800&h=600&c=7`")
content = content.replace("- `[ ]` Test the frontend to ensure images load correctly and look good.", "- `[x]` Test the frontend to ensure images load correctly and look good.")

with open("/Users/bhawna/.gemini/antigravity-ide/brain/1112063e-d36f-414a-9c86-9a578decd29e/task.md", "w") as f:
    f.write(content)
