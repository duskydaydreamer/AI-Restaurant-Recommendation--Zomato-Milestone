"""
Image fetching service using Zomato URL scraping.
"""

import logging
import urllib.request
import re

logger = logging.getLogger(__name__)

def fetch_restaurant_image_url(zomato_url: str) -> str:
    """Fetch a single image URL for a restaurant by scraping its Zomato page."""
    if not zomato_url:
        return ""
    
    try:
        req = urllib.request.Request(
            zomato_url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        )
        html = urllib.request.urlopen(req, timeout=5).read().decode("utf-8")
        
        # Look for Zomato image URLs in the HTML
        matches = re.findall(r"https://b\.zmtcdn\.com/data/pictures/[a-zA-Z0-9/_.-]+\.jpg", html)
        if matches:
            # Try to avoid the heavily blurred/featured background variants if possible
            for m in matches:
                if 'featured_v2' not in m and 'crop=' not in m:
                    return m
            return matches[0]
            
    except Exception as e:
        logger.warning("Failed to fetch image from Zomato URL %s: %s", zomato_url, e)
        
    return ""
