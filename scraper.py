import os
import csv
import time
from playwright.sync_api import sync_playwright

def hunt_leads():
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    
    with sync_playwright() as p:
        # Launch standard chromium
        browser = p.chromium.launch(headless=True)
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )

        # --- THE STEALTH SHIELD ---
        # We manually inject JS to hide automation signatures
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """)

        page = context.new_page()
        print(f"🕵️ Hunter starting for: {query}")
        
        # Navigate directly to Google Maps
        page.goto(f"https://www.google.com/maps/search/louvre+museum+in+paris/?hl=en{query.replace(' ', '+')}")
        
        # Give Google a moment to breathe (Human-like wait)
        time.sleep(5)

        # Logic to find listings
        leads = []
        try:
            # Wait for any article (business listing) to appear
            page.wait_for_selector('div[role="article"]', timeout=20000)
            
            listings = page.locator('div[role="article"]').all()
            print(f"📋 Found {len(listings)} businesses. Filtering...")

            for listing in listings[:15]:
                # Business Name
                name = listing.get_attribute("aria-label")
                if not name: continue
                
                # Check for Website - Google uses data-item-id="authority" for the globe icon/link
                has_website = listing.locator('a[data-item-id="authority"]').count() > 0
                
                if not has_website:
                    # Target found! 
                    leads.append({"Name": name, "Phone": "Check Details"})
                    print(f"🎯 Target Found: {name}")

        except Exception as e:
            print(f"❌ Error during scrape: {e}")

        # Save to CSV
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        print(f"✅ Finished! Found {len(leads)} leads.")
        browser.close()

if __name__ == "__main__":
    hunt_leads()
