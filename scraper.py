import os
import csv
from playwright.sync_api import sync_playwright

def hunt_leads():
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a more realistic browser context
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"Searching for: {query}")
        search_url = f"http://googleusercontent.com/maps.google.com/5{query.replace(' ', '+')}"
        page.goto(search_url)
        
        # 1. Handle Google "Consent" or "I agree" buttons if they appear
        try:
            if page.get_by_role("button", name="Accept all").is_visible():
                page.get_by_role("button", name="Accept all").click()
        except:
            pass

        page.wait_for_timeout(5000)

        # 2. Force the sidebar to scroll to load listings
        # We target the main scrollable container in the sidebar
        for _ in range(3):
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(2000)

        leads = []
        
        # 3. Get all links that look like business listings
        # Google Maps listings usually contain '/maps/place/' in the URL
        listings = page.locator('a[href*="/maps/place/"]').all()
        print(f"Found {len(listings)} potential listings...")

        for listing in listings[:15]: # Check first 15
            try:
                name = listing.get_attribute("aria-label")
                if not name:
                    continue
                
                listing.click()
                page.wait_for_timeout(3000)

                # 4. Logic: Check if Website button is MISSING
                # Google uses 'authority' as the ID for the website link
                has_website = page.locator('a[data-item-id="authority"]').is_visible()
                
                if not has_website:
                    # Try to get phone number
                    phone = "N/A"
                    phone_el = page.locator('button[data-item-id^="phone:tel"]').first
                    if phone_el.is_visible():
                        phone = phone_el.inner_text()

                    leads.append({"Name": name, "Phone": phone})
                    print(f"✅ Lead Added: {name}")
            except Exception as e:
                print(f"Error checking listing: {e}")
                continue

        # Save results
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
            
        print(f"Scrape complete. Total leads found: {len(leads)}")
        browser.close()

if __name__ == "__main__":
    hunt_leads()
