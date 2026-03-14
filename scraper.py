import os
import csv
import random
import time
from playwright_extra import sync_playwright
from puppeteer_extra_plugin_stealth import StealthPlugin

def hunt_leads():
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    
    # 1. Initialize the Stealth Plugin
    stealth = StealthPlugin()
    
    # 2. Use playwright_extra to 'wrap' standard playwright with stealth
    with sync_playwright().use(stealth) as p:
        # 3. Launch with a few "human" arguments
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        # 4. Create a context with a realistic user agent
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()
        print(f"🕵️ Hunter starting for: {query}")
        
        # Navigate to Google Maps
        page.goto(f"https://www.google.com/maps/search/{query.replace(' ', '+')}")
        
        # Wait for the results to load (Wait for the 'feed' container)
        try:
            page.wait_for_selector('div[role="feed"]', timeout=20000)
        except:
            print("❌ Timeout: Google Maps didn't load the results list.")
            browser.close()
            return

        # 5. Mimic Human Scrolling
        # We scroll down in small, random chunks to load listings
        for _ in range(3):
            scroll_dist = random.randint(700, 1000)
            page.mouse.wheel(0, scroll_dist)
            time.sleep(random.uniform(1.5, 3.0))

        leads = []
        # Get all business listings
        listings = page.locator('div[role="article"]').all()
        print(f"📋 Found {len(listings)} businesses. Filtering...")

        for listing in listings[:15]:
            try:
                # Get name
                name = listing.get_attribute("aria-label")
                if not name:
                    continue
                
                # Logic: Check if the 'Website' button is visible
                # In 2026, the data-item-id 'authority' is the most reliable check
                has_website = listing.locator('a[data-item-id="authority"]').is_visible()
                
                if not has_website:
                    # Try to grab the phone number from the listing summary
                    phone = "Contact Info in Details"
                    # Using a generic text-search for phone patterns
                    phone_match = listing.get_by_text(r"\+91|0\d{10}").first
                    if phone_match.is_visible():
                        phone = phone_match.inner_text()

                    leads.append({"Name": name, "Phone": phone})
                    print(f"🎯 Target Found: {name}")

            except Exception:
                continue

        # 6. Save results
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        print(f"✅ Finished! Scraped {len(leads)} potential clients.")
        browser.close()

if __name__ == "__main__":
    hunt_leads()
