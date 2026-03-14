import os
import csv
import time
from playwright.sync_api import sync_playwright

def hunt_leads():
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    kolkata_center = "@22.5726,88.3639,13z"
    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/{kolkata_center}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print(f"🕵️ Hunter starting for: {query}")
        page.goto(search_url)
        
        # 1. Wait until the results actually appear
        try:
            page.wait_for_selector('div[role="article"]', timeout=30000)
        except:
            print("❌ Timeout: No results appeared. Check debug_view.png")
            page.screenshot(path="debug_view.png")
            browser.close()
            return

        # 2. Scroll slowly to load metadata
        for _ in range(3):
            page.mouse.wheel(0, 2000)
            time.sleep(2)

        leads = []
        # 3. Find all business containers
        listings = page.locator('div[role="article"]').all()
        print(f"📋 Found {len(listings)} listings. Filtering...")

        for listing in listings:
            try:
                name = listing.get_attribute("aria-label")
                if not name: continue

                # --- THE "OUTBOUND LINK" FILTER ---
                # We find all <a> tags inside this specific listing
                all_links = listing.locator('a').all()
                has_external_site = False
                
                for link in all_links:
                    href = link.get_attribute("href")
                    if href and "http" in href and "google.com" not in href:
                        # If a link exists that doesn't belong to Google, it's a website
                        has_external_site = True
                        break

                if has_external_site:
                    print(f"⏭️ Skipping {name} (External site found)")
                    continue

                # 4. If no external site found, it's a lead
                phone = "N/A"
                phone_el = listing.locator('span.Us79be').first
                if phone_el.count() > 0:
                    phone = phone_el.inner_text()

                leads.append({"Name": name, "Phone": phone})
                print(f"🎯 Target Found: {name}")

            except Exception:
                continue

        # Save results
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        page.screenshot(path="debug_view.png")
        print(f"✅ Done! Found {len(leads)} leads.")
        browser.close()

if __name__ == "__main__":
    hunt_leads()
