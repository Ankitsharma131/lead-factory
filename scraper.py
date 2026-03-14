import os
import csv
import time
from playwright.sync_api import sync_playwright

def hunt_leads():
    # 1. Config & Target
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    search_query = query.replace(' ', '+')
    # Forces Google to center on Kolkata (22.57, 88.36) to avoid France results
    search_url = f"https://www.google.com/maps/search/{search_query}/@22.5726,88.3639,13z"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"🕵️ Hunter starting for: {query}")
        page.goto(search_url)
        
        # Handle Potential Cookie/Consent screens
        try:
            page.get_by_role("button", name="Accept all").click(timeout=5000)
        except:
            pass

        # Wait for the results to actually appear
        try:
            page.wait_for_selector('div[role="article"]', timeout=15000)
        except:
            page.screenshot(path="debug_view.png")
            print("❌ Timeout: No businesses found in view.")
            browser.close()
            return

        # Capture live view for Telegram
        page.screenshot(path="debug_view.png")

        leads = []
        try:
            # 2. Scroll the sidebar to load more results
            feed = page.locator('div[role="feed"]')
            if feed.count() > 0:
                for _ in range(3):
                    feed.evaluate("el => el.scrollBy(0, 3000)")
                    time.sleep(2)

            # 3. Process all found listings
            listings = page.locator('div[role="article"]').all()
            print(f"📋 Found {len(listings)} businesses. Filtering for those without websites...")

            for listing in listings[:20]: # Process top 20
                name = listing.get_attribute("aria-label")
                if not name: continue

                # --- ADVANCED WEBSITE FILTER ---
                # Check 1: Official 'Website' button
                has_authority = listing.locator('a[data-item-id="authority"]').count() > 0
                
                # Check 2: Text search for URLs in the card (e.g., .com, .in)
                card_text = listing.inner_text().lower()
                has_url_text = any(ext in card_text for ext in ['.com', '.in', '.org', '.net', '.co'])

                if not has_authority and not has_url_text:
                    # Target Found! Now get the phone.
                    try:
                        listing.click()
                        time.sleep(2) # Wait for sidebar detail pane
                        
                        phone = "N/A"
                        # Extract from the 'phone:tel' button attribute
                        phone_el = page.locator('button[data-item-id^="phone:tel"]').first
                        if phone_el.is_visible():
                            phone = phone_el.get_attribute("data-item-id").replace("phone:tel:", "")
                        
                        leads.append({"Name": name, "Phone": phone})
                        print(f"🎯 Lead Found: {name} | Phone: {phone}")
                        
                        # Reset for next click
                        page.keyboard.press("Escape")
                    except:
                        continue
                else:
                    print(f"⏩ Skipping: {name} (Has Website)")

        except Exception as e:
            print(f"❌ Error during scan: {e}")

        # 4. Save to CSV
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        print(f"✅ Finished! Found {len(leads)} valid leads.")
        browser.close()

if __name__ == "__main__":
    hunt_leads()
