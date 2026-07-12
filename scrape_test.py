import asyncio
import json
import re
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Randomize user agent slightly
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        # Navigate to a Zomato URL
        url = "https://www.zomato.com/bangalore/santé-spa-cuisine-indiranagar"
        await page.goto(url, wait_until="domcontentloaded")
        content = await page.content()
        
        # Check if we got blocked
        if "Access Denied" in content or "Captcha" in content:
            print("BLOCKED")
            await browser.close()
            return
            
        # Try to extract the PRELOADED_STATE
        match = re.search(r"window\.__PRELOADED_STATE__ = JSON\.parse\(\"(.*?)\"\);", content)
        if match:
            print("FOUND PRELOADED STATE")
            raw_json = match.group(1).replace('\\"', '"').replace('\\\\', '\\')
            try:
                data = json.loads(raw_json)
                # print some keys to verify
                print("KEYS:", list(data.keys())[:5])
                
                # find images
                images = []
                for k, v in data.items():
                    if isinstance(v, dict):
                        for sub_k, sub_v in v.items():
                            if isinstance(sub_v, dict) and "url" in sub_v and "zmtcdn.com/data/pictures" in str(sub_v["url"]):
                                images.append(sub_v["url"])
                print("IMAGES:", len(images), images[:2])
            except Exception as e:
                print("JSON Parse error", e)
        else:
            print("PRELOADED STATE NOT FOUND")
            
        await browser.close()

asyncio.run(main())
