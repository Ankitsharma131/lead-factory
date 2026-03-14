import os
import csv
import time
from playwright.sync_api import sync_playwright

def hunt_leads():
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    # Native Google Maps search URL with Kolkata focus
    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/@22.5726,88.3639,13z"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print(f"🕵️ Hunter focusing on Kolkata...")
        page.goto(search_url)
        
        # 1. CRITICAL: Wait for the results to actually appear in the DOM
        try:
            page.wait_for_selector('div[role="article"]', timeout=15000)
        except:
            print("❌ Results didn't load in time.")
            page.screenshot(path="debug_view.png")
            browser.close()
            return

        # 2. Manual Scroll to ensure all 10+ results are loaded
        scrollable = page.locator('div[role="feed"]')
        for _ in range(2):
            page.mouse.wheel(0, 2000)
            time.sleep(2)

        page.screenshot(path="debug_view.png") # Final capture of the list

        leads = []
        # 3. Use the most stable selector for the business cards
        listings = page.locator('div[role="article"]').all()
        print(f"📋 Found {len(listings)} businesses. Filtering...")

        for listing in listings[:10]:
            try:
                # Extract business name from the aria-label
                name = listing.get_attribute("aria-label")
                if not name: continue
                
                # WEBSITE CHECK: We check if the 'Website' link is ABSENT
                # Google uses a[data-item-id="authority"] for the globe icon
                website_link = listing.locator('a[data-item-id="authority"]')
                
                if website_link.count() == 0:
                    # Target Found! No website button.
                    # For now, let's grab the phone number directly from the listing text
                    # (Google often shows it right under the name in the list)
                    phone = "Found - Check Details"
                    
                    leads.append({"Name": name, "Phone": phone})
                    print(f"🎯 Target Found: {name}")
            except:
                continue

        # 4. Save to CSV
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        print(f"✅ Success! Found {len(leads)} target businesses.")
        browser.close()

if __name__ == "__main__":
    hunt_leads()
