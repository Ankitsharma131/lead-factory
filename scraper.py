import os
import csv
import time
from playwright.sync_api import sync_playwright

def hunt_leads():
    # 1. Configuration
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    # Coordinates for Kolkata to override GitHub's server location
    kolkata_coords = "@22.5726,88.3639,13z"
    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/{kolkata_coords}"

    with sync_playwright() as p:
        # 2. Setup Browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"🕵️ Hunter starting for: {query}")
        page.goto(search_url)
        
        # Wait for page to stabilize
        time.sleep(5)
        
        # Handle "Accept all" if it appears (common on European runners)
        try:
            page.get_by_role("button", name="Accept all").click(timeout=3000)
        except:
            pass

        # 3. Scroll the results feed
        try:
            page.wait_for_selector('div[role="feed"]', timeout=10000)
            for _ in range(3):
                page.mouse.wheel(0, 3000)
                time.sleep(2)
        except:
            print("⚠️ Sidebar feed not found, taking screenshot...")
            page.screenshot(path="debug_view.png")

        leads = []
        # 4. Filter and Extract
        listings = page.locator('div[role="article"]').all()
        print(f"📋 Found {len(listings)} businesses. Applying filters...")

        for listing in listings:
            try:
                name = listing.get_attribute("aria-label")
                if not name: continue

                # --- THE TRIPLE FILTER ---
                # Check 1: The 'Website' globe icon
                has_icon = listing.locator('a[data-item-id="authority"]').count() > 0
                
                # Check 2: The text 'Website' appearing as a link
                has_text_link = listing.get_by_role("link", name="Website").count() > 0
                
                # Check 3: Check if it's just a social media link (Optional but helpful)
                is_social_only = False
                if has_icon:
                    url = listing.locator('a[data-item-id="authority"]').get_attribute("href").lower()
                    social_sites = ['facebook.com', 'instagram.com', 'indiamart.com', 'justdial.com']
                    if any(site in url for site in social_sites):
                        is_social_only = True

                # LOGIC: If it has a real site (Icon or Text) AND it's not a social site... SKIP it.
                if (has_icon or has_text_link) and not is_social_only:
                    print(f"⏭️ Skipping {name} (Has professional website)")
                    continue

                # 5. Extract Phone if it passed the filter
                phone = "N/A"
                # Locate the phone span by the common 'Us79be' class or text pattern
                phone_el = listing.locator('span.Us79be').first
                if phone_el.count() > 0:
                    phone = phone_el.inner_text()

                leads.append({"Name": name, "Phone": phone})
                print(f"🎯 Lead Captured: {name} | Phone: {phone}")

            except Exception as e:
                continue

        # 6. Save results & Debug Screenshot
        page.screenshot(path="debug_view.png")
        
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        print(f"✅ Scrape finished. {len(leads)} leads ready for Phase 2.")
        browser.close()

if __name__ == "__main__":
    hunt_leads()
