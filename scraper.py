import os
import csv
import time
from playwright.sync_api import sync_playwright

def hunt_leads():
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    # Forces Google to center on Kolkata
    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/@22.5726,88.3639,13z"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"🕵️ Hunter starting for: {query}")
        page.goto(search_url)
        
        # Wait for the page to load
        time.sleep(5)
        
        # 1. Take a debug screenshot
        page.screenshot(path="debug_view.png")
        print("📸 Screenshot captured as debug_view.png")

        leads = []
        try:
            # 2. Scroll the results panel
            for _ in range(3):
                page.mouse.wheel(0, 3000)
                time.sleep(2)

            # 3. Find listings
            listings = page.locator('div[role="article"]').all()
            print(f"📋 Found {len(listings)} listings. Filtering...")

            for listing in listings[:10]:
                name = listing.get_attribute("aria-label")
                if not name: continue
                
                # Check for website
                has_website = listing.locator('a[data-item-id="authority"]').count() > 0
                
                if not has_website:
                    leads.append({"Name": name, "Phone": "Check Image"})
                    print(f"🎯 Target Found: {name}")

        except Exception as e:
            print(f"❌ Error: {e}")

        # 4. Save results
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        browser.close()

if __name__ == "__main__":
    hunt_leads()
