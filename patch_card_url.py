import re

with open("frontend/src/components/RecommendationCard.jsx", "r") as f:
    content = f.read()

old_buttons = """        <div className="mt-auto flex gap-sm pt-sm">
          <button className="bg-primary text-on-primary px-md py-sm rounded-lg font-label-md shadow-sm hover:bg-[#c92e3a] transition-colors flex-1 text-center">Book Table</button>
          <button className="bg-white border border-primary text-primary px-md py-sm rounded-lg font-label-md hover:bg-primary/5 transition-colors flex-1 text-center">View Details</button>
        </div>"""

new_buttons = """        <div className="mt-auto flex gap-sm pt-sm">
          <a href={rec.url || '#'} target="_blank" rel="noopener noreferrer" className="bg-primary text-on-primary px-md py-sm rounded-lg font-label-md shadow-sm hover:bg-[#c92e3a] transition-colors flex-1 text-center block">Book Table</a>
          <a href={rec.url || '#'} target="_blank" rel="noopener noreferrer" className="bg-white border border-primary text-primary px-md py-sm rounded-lg font-label-md hover:bg-primary/5 transition-colors flex-1 text-center block">View Details</a>
        </div>"""

content = content.replace(old_buttons, new_buttons)

with open("frontend/src/components/RecommendationCard.jsx", "w") as f:
    f.write(content)
