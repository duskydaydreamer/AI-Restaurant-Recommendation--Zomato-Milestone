import re

with open("frontend/src/App.jsx", "r") as f:
    content = f.read()

# Replace ClocheIllustration
old_cloche = '<div className="relative w-24 h-24 flex-shrink-0 flex items-center justify-center">'
new_cloche = '<div className="relative w-16 h-16 sm:w-20 sm:h-20 flex-shrink-0 flex items-center justify-center opacity-90">'
content = content.replace(old_cloche, new_cloche)

# Extract and Replace AI Summary Block
old_summary_block_pattern = r'\{/\*\s*AI Summary Block\s*\*/\}(.*?)(?=\{/\*\s*Results List\s*\*/\})'
old_summary_block = re.search(old_summary_block_pattern, content, re.DOTALL)

if old_summary_block:
    new_summary_block = """{/* AI Summary Block */}
                  <div className="bg-primary/5 border border-primary/10 border-l-4 border-l-primary rounded-xl p-lg shadow-sm flex flex-row items-center gap-md sm:gap-lg mb-lg">
                    <ClocheIllustration />
                    <div className="flex flex-col gap-xs max-w-[800px]">
                      <h3 className="font-headline-md text-headline-md text-on-surface font-bold m-0 leading-tight">
                        I found {Math.min(results.recommendations?.length || 0, topK)} options for you
                      </h3>
                      <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed m-0">
                        Based on your budget and preferences, here are restaurants worth exploring in <span className="font-medium text-on-surface capitalize">{location}</span>.
                      </p>
                    </div>
                  </div>
                  """
    content = content[:old_summary_block.start()] + new_summary_block + content[old_summary_block.end():]
else:
    print("Could not find AI Summary Block")

with open("frontend/src/App.jsx", "w") as f:
    f.write(content)
