import os
import csv
import time
from playwright.sync_api import sync_playwright

def hunt_leads():
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    kolkata_center = "@22.5726,88.3639,13z"
    search_url = f"http://googleusercontent.com/maps.google.com/search?q={query.replace(' ', '+')}/{kolkata_center}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print(f"🕵️ Hunter focusing on Kolkata...")
        page.goto(search_url)
        time.sleep(5) # Allow map to load
        
        # Take the debug screenshot
        page.screenshot(path="debug_view.png")

        leads = []
        # Find all business card containers
        listings = page.locator('div[role="article"]').all()

        for listing in listings[:10]:
            try:
                name = listing.get_attribute("aria-label")
                if not name: continue
                
                # WEBSITE CHECK: If the 'Website' globe icon is MISSING
                has_website = listing.locator('a[data-item-id="authority"]').count() > 0
                
                if not has_website:
                    # CLICK to open the sidebar for the phone number
                    listing.click()
                    time.sleep(2) # Wait for sidebar
                    
                    phone = "No Phone Listed"
                    # Google uses a button with a data-item-id that starts with 'phone:tel'
                    phone_el = page.locator('button[data-item-id^="phone:tel"]').first
                    if phone_el.is_visible():
                        phone = phone_el.get_attribute("data-item-id").replace("phone:tel:", "")

                    leads.append({"Name": name, "Phone": phone})
                    print(f"🎯 Lead Found: {name} | Phone: {phone}")
                    
                    # Optional: Press Escape to close sidebar and reset for next click
                    page.keyboard.press("Escape")
            except:
                continue

        # Save results
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        browser.close()

if __name__ == "__main__":
    hunt_leads()
