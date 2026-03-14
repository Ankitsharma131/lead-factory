import os
import csv
import time
from playwright.sync_api import sync_playwright

def hunt_leads():
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    # Using the coordinates we know work for Kolkata
    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/@22.5726,88.3639,13z"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print(f"🕵️ Searching for: {query}")
        page.goto(search_url)
        page.wait_for_selector('div[role="article"]', timeout=15000)

        # Scroll to load the list properly
        for _ in range(3):
            page.mouse.wheel(0, 3000)
            time.sleep(2)

        leads = []
        listings = page.locator('div[role="article"]').all()

        for listing in listings[:20]:
            try:
                name = listing.get_attribute("aria-label")
                if not name: continue
                
                # Check for the presence of a website link
                # In your screenshot, businesses WITH sites have a specific link container
                has_website = listing.locator('a[data-item-id="authority"]').count() > 0
                
                if not has_website:
                    # CLICK to confirm it's actually missing (looking for "Add website")
                    listing.click()
                    time.sleep(2)
                    
                    # If the sidebar shows "Add website", it's 100% a lead
                    add_website_btn = page.get_by_text("Add website")
                    
                    if add_website_btn.is_visible():
                        print(f"🎯 GOLD MINE: {name} (Confirmed No Website)")
                        
                        # Get phone number from sidebar
                        phone = "N/A"
                        phone_el = page.locator('button[data-item-id^="phone:tel"]').first
                        if phone_el.is_visible():
                            phone = phone_el.get_attribute("data-item-id").replace("phone:tel:", "")
                        
                        leads.append({"Name": name, "Phone": phone})
                        page.keyboard.press("Escape")
                else:
                    print(f"⏩ Skipping {name} (Has Website)")
            except:
                continue

        # Save to CSV
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        page.screenshot(path="debug_view.png")
        print(f"✅ Found {len(leads)} businesses that need a website.")
        browser.close()

if __name__ == "__main__":
    hunt_leads()
