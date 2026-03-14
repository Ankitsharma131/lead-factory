import os
import csv
import time
from playwright.sync_api import sync_playwright

def hunt_leads():
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    kolkata_coords = "@22.5726,88.3639,13z"
    # Using the native search path
    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/{kolkata_coords}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print(f"🕵️ Hunter starting...")
        page.goto(search_url)
        time.sleep(5) 

        # Scroll to load businesses
        for _ in range(3):
            page.mouse.wheel(0, 3000)
            time.sleep(2)

        leads = []
        listings = page.locator('div[role="article"]').all()
        print(f"📋 Found {len(listings)} businesses. Running Deep-Filter...")

        for listing in listings:
            try:
                name = listing.get_attribute("aria-label")
                if not name: continue

                # --- THE DEEP FILTER ---
                # 1. Search for any text that says "Website"
                # 2. Search for the globe icon (authority)
                # 3. Search for any 'a' tag that has an 'aria-label' containing "Website"
                
                has_website_text = listing.get_by_text("Website", exact=False).count() > 0
                has_website_id = listing.locator('a[data-item-id="authority"]').count() > 0
                has_website_label = listing.locator('a[aria-label*="Website"]').count() > 0
                
                # If ANY of these are true, the business has a site.
                if has_website_text or has_website_id or has_website_label:
                    print(f"⏭️ Skipping {name} (Website Found)")
                    continue

                # If no website signs were found, it's a lead
                phone = "N/A"
                phone_el = listing.locator('span.Us79be').first
                if phone_el.count() > 0:
                    phone = phone_el.inner_text()

                leads.append({"Name": name, "Phone": phone})
                print(f"🎯 Target Found: {name}")

            except Exception:
                continue

        # Final check: Screenshot to see if the skip logic actually ran
        page.screenshot(path="debug_view.png")
        
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        print(f"✅ Scrape finished. {len(leads)} leads found.")
        browser.close()

if __name__ == "__main__":
    hunt_leads()
