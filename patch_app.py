with open("frontend/src/App.jsx", "r") as f:
    content = f.read()

old_app = """                  {/* AI Summary Block */}
                  <div className="bg-[#fef2f2] border border-[#fecaca] border-l-4 border-l-primary rounded-xl p-6 shadow-sm flex items-center gap-6 mb-6">
                    <ClocheIllustration />
                    <div className="flex flex-col gap-1 text-left">
                      <h3 className="font-headline-md text-headline-md text-on-surface font-bold">
                        I found {Math.min(results.recommendations?.length || 0, topK)} places for you
                      </h3>
                      <p className="font-body-md text-body-md text-on-surface-variant">
                        Based on your budget and preferences, here are restaurants worth exploring in {selectedLocation}.
                      </p>
                    </div>
                  </div>
                  {/* Results List */}
                  <div className="space-y-[26px]">
                    {results.recommendations?.slice(0, topK).map(rec => (
                      <RecommendationCard 
                        key={rec.restaurant_id} 
                        rec={rec} 
                      />
                    ))}
                  </div>"""

new_app = """                  {/* AI Summary Block */}
                  <div className="bg-primary/5 border border-primary/10 border-l-4 border-l-primary rounded-xl p-md sm:p-lg shadow-sm flex flex-col sm:flex-row items-center sm:items-start gap-md sm:gap-lg mb-lg">
                    <ClocheIllustration />
                    <div className="flex flex-col gap-xs pt-xs text-center sm:text-left">
                      <h3 className="font-headline-md text-headline-md text-on-surface font-bold">
                        I found {Math.min(results.recommendations?.length || 0, topK)} exceptional options for you.
                      </h3>
                      <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed">
                        {results.summary}
                      </p>
                    </div>
                  </div>
                  {/* Results List */}
                  <div className="space-y-lg">
                    {results.recommendations?.slice(0, topK).map(rec => (
                      <RecommendationCard 
                        key={rec.restaurant_id} 
                        rec={rec} 
                      />
                    ))}
                  </div>"""

content = content.replace(old_app, new_app)

with open("frontend/src/App.jsx", "w") as f:
    f.write(content)
