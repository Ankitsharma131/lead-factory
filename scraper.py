import os
import csv
import time
from playwright.sync_api import sync_playwright

def hunt_leads():
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/@22.5726,88.3639,13z"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print(f"🕵️ Hunter starting for: {query}")
        page.goto(search_url)
        
        try:
            page.wait_for_selector('div[role="article"]', timeout=15000)
        except:
            print("❌ SKIP REASON: Page failed to load any business listings.")
            browser.close()
            return

        time.sleep(3)
        leads = []
        listings = page.locator('div[role="article"]').all()

        for listing in listings[:15]:
            try:
                name = listing.get_attribute("aria-label")
                if not name:
                    print("⏩ SKIP REASON: Business name could not be read from aria-label.")
                    continue
                
                # Check for website link in the list card
                website_btn = listing.locator('a[data-item-id="authority"]')
                
                if website_btn.count() > 0:
                    # REASON 1: Website already exists in the list view
                    print(f"⏩ SKIP: {name} | REASON: Already has a 'Website' button in list view.")
                    continue

                # If no button, we deep-check the sidebar
                listing.click()
                time.sleep(2)

                # Check for "Add website" text in the sidebar
                add_website_visible = page.get_by_text("Add website").is_visible()
                
                if add_website_visible:
                    # SUCCESS: Both checks passed
                    phone = "N/A"
                    phone_el = page.locator('button[data-item-id^="phone:tel"]').first
                    if phone_el.is_visible():
                        phone = phone_el.get_attribute("data-item-id").replace("phone:tel:", "")
                    
                    leads.append({"Name": name, "Phone": phone})
                    print(f"🎯 ADDED: {name} | REASON: No website button AND 'Add website' text found.")
                else:
                    # REASON 2: No website button, but the sidebar doesn't offer "Add website"
                    print(f"⏩ SKIP: {name} | REASON: No website button, but sidebar does NOT show 'Add website' text.")
                
                page.keyboard.press("Escape")
            except Exception as e:
                print(f"⏩ SKIP: Error processing listing | REASON: {str(e)}")
                continue

        # Save to CSV
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        print(f"✅ FINAL REPORT: Scraped {len(leads)} leads into the CSV.")
        browser.close()

if __name__ == "__main__":
    hunt_leads()
