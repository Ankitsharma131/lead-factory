import os
import csv
import time
from playwright.sync_api import sync_playwright

def hunt_leads():
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    search_query = query.replace(' ', '+')
    # Hard-coded Kolkata Coordinates
    search_url = f"https://www.google.com/maps/search/{search_query}/@22.5726,88.3639,13z"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print(f"🕵️ Deep Hunter starting for: {query}")
        page.goto(search_url)
        time.sleep(5) 

        leads = []
        try:
            # Scroll to load the initial list
            feed = page.locator('div[role="feed"]')
            if feed.count() > 0:
                feed.evaluate("el => el.scrollBy(0, 2000)")
                time.sleep(2)

            listings = page.locator('div[role="article"]').all()
            print(f"📋 Scanning {len(listings)} businesses deeply...")

            for listing in listings[:15]:
                try:
                    name = listing.get_attribute("aria-label")
                    if not name: continue

                    # --- STEP 1: CLICK TO OPEN FULL DETAILS ---
                    listing.click()
                    time.sleep(2.5) # Give the sidebar time to load completely

                    # --- STEP 2: LOOK FOR WEBSITE IN THE SIDEBAR ---
                    # We check the 'authority' ID which is only in the detail pane
                    detail_pane = page.locator('div[role="main"]')
                    website_el = detail_pane.locator('a[data-item-id="authority"]')
                    
                    # Also check for any text that looks like a URL in the sidebar
                    sidebar_text = detail_pane.inner_text().lower()
                    has_url = any(ext in sidebar_text for ext in ['.com', '.in', '.org', '.net', '.co'])

                    if website_el.count() == 0 and not has_url:
                        # --- STEP 3: NO WEBSITE FOUND -> GRAB PHONE ---
                        phone = "N/A"
                        phone_el = detail_pane.locator('button[data-item-id^="phone:tel"]').first
                        if phone_el.is_visible():
                            phone = phone_el.get_attribute("data-item-id").replace("phone:tel:", "")
                        
                        leads.append({"Name": name, "Phone": phone})
                        print(f"🎯 VALID LEAD (No Website): {name} | {phone}")
                    else:
                        print(f"⏩ Skipping {name} (Website detected in sidebar)")

                    # Reset for next listing
                    page.keyboard.press("Escape")
                    time.sleep(0.5)

                except Exception:
                    continue

        except Exception as e:
            print(f"❌ Error: {e}")

        # Save to CSV
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        page.screenshot(path="debug_view.png")
        print(f"✅ Scrape finished. Found {len(leads)} valid targets.")
        browser.close()

if __name__ == "__main__":
    hunt_leads()
