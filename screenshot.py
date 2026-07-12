import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:5173")
        
        # Wait for React to mount and user to be able to type
        await page.wait_for_selector("textarea", timeout=10000)
        
        # Fill the query
        await page.fill("textarea", "I want nice indian food in indiranagar for a high budget")
        
        # Click submit
        await page.click(".glow-button")
        
        # Wait for the results to load (RecommendationCard uses article tag)
        await page.wait_for_selector("article", timeout=15000)
        
        # Take a screenshot
        await page.screenshot(path="frontend_screenshot.png", full_page=True)
        await browser.close()

asyncio.run(main())
