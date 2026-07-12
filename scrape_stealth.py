import asyncio
import json
import re
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth_async(page)
        
        url = "https://www.zomato.com/bangalore/santé-spa-cuisine-indiranagar"
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            content = await page.content()
            
            if "Access Denied" in content or "Captcha" in content:
                print("BLOCKED")
            else:
                match = re.search(r"window\.__PRELOADED_STATE__ = JSON\.parse\(\"(.*?)\"\);", content)
                if match:
                    print("FOUND PRELOADED STATE")
                else:
                    print("PRELOADED STATE NOT FOUND")
        except Exception as e:
            print("ERROR", type(e).__name__)
        
        await browser.close()

asyncio.run(main())
