import os
import csv
import time
from playwright.sync_api import sync_playwright

def hunt_leads():
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    search_query = query.replace(' ', '+')
    # Corrected URL structure
    search_url = f"https://www.google.com/maps/search/{search_query}/@22.5726,88.3639,13z"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print(f"🕵️ Hunter starting for: {query}")
        
        # Go to the URL
        page.goto(search_url)
        
        # 1. FIX: Wait for the results sidebar OR an article to appear
        # We use a 15-second timeout and a specific selector instead of 'networkidle'
        try:
            page.wait_for_selector('div[role="article"]', timeout=15000)
            print("✅ Results loaded successfully.")
        except:
            print("⚠️ Results didn't load in time, taking screenshot to see why...")
            page.screenshot(path="debug_view.png")
            # If it timed out, we still try to proceed
        
        time.sleep(2) # Final buffer for rendering
        page.screenshot(path="debug_view.png")

        leads = []
        try:
            # 2. Find and Scroll
            # We target the feed container to scroll
            feed = page.locator('div[role="feed"]')
            if feed.count() > 0:
                for _ in range(3):
                    feed.evaluate("el => el.scrollBy(0, 3000)")
                    time.sleep(2)

            # 3. Process listings
            listings = page.locator('div[role="article"]').all()
            print(f"📋 Found {len(listings)} listings. Filtering...")

            for listing in listings[:10]:
                name = listing.get_attribute("aria-label")
                if not name: continue
                
                # Check for website
                has_website = listing.locator('a[data-item-id="authority"]').count() > 0
                
                if not has_website:
                    # Click and grab phone from detail pane
                    listing.click()
                    time.sleep(2)
                    
                    phone = "N/A"
                    phone_el = page.locator('button[data-item-id^="phone:tel"]').first
                    if phone_el.is_visible():
                        phone = phone_el.get_attribute("data-item-id").replace("phone:tel:", "")

                    leads.append({"Name": name, "Phone": phone})
                    print(f"🎯 Lead: {name} | Phone: {phone}")
                    page.keyboard.press("Escape")

        except Exception as e:
            print(f"❌ Error during scan: {e}")

        # 4. Save
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        browser.close()

if __name__ == "__main__":
    hunt_leads()
