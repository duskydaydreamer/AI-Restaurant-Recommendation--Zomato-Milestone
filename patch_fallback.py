import re

with open("frontend/src/components/RecommendationCard.jsx", "r") as f:
    content = f.read()

old_func = """  const getCuisineImage = (cuisinesList) => {
    if (!cuisinesList || cuisinesList.length === 0) return '/images/luxury.png';
    const primary = cuisinesList[0].toLowerCase();
    
    if (primary.includes('italian') || primary.includes('pizza') || primary.includes('pasta')) return '/images/italian.png';
    if (primary.includes('indian') || primary.includes('mughlai') || primary.includes('biryani') || primary.includes('andhra') || primary.includes('kerala')) return '/images/indian.png';
    if (primary.includes('cafe') || primary.includes('dessert') || primary.includes('bakery') || primary.includes('beverage')) return '/images/cafe.png';
    if (primary.includes('asian') || primary.includes('chinese') || primary.includes('japanese') || primary.includes('sushi') || primary.includes('thai')) return '/images/asian.png';
    
    return '/images/luxury.png';
  };"""

new_func = """  const getCuisineImage = (cuisinesList) => {
    // Fallback to high-quality generic restaurant photos if Bing fails
    return 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80';
  };"""

content = content.replace(old_func, new_func)

with open("frontend/src/components/RecommendationCard.jsx", "w") as f:
    f.write(content)
