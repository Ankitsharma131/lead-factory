import os
import csv
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def hunt_leads():
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    
    with sync_playwright() as p:
        # PROXY PLACEHOLDER: Uncomment the lines below if GitHub gets blocked
        # proxy_settings = {
        #     "server": "http://your-proxy-address:port",
        #     "username": "your-username",
        #     "password": "your-password"
        # }
        # browser = p.chromium.launch(headless=True, proxy=proxy_settings)
        
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        stealth_sync(page)
        
        print(f"Opening Google Maps for: {query}")
        page.goto(f"https://www.google.com/maps/search/{query.replace(' ', '+')}")
        
        # Handling the basic 'Accept all' cookie banner if it blocks the view
        try:
            page.get_by_role("button", name="Accept all").click(timeout=3000)
        except:
            pass

        # Wait for the results panel to appear
        page.wait_for_selector('div[role="feed"]', timeout=10000)

        # Scroll to load businesses
        scrollable = page.locator('div[role="feed"]')
        for _ in range(3):
            page.evaluate('(el) => el.scrollTop = el.scrollHeight', scrollable.element_handle())
            time.sleep(2)

        leads = []
        # Modern 2026 listing container selector
        listings = page.locator('div[role="article"]').all()
        print(f"Scanning {len(listings)} businesses...")

        for listing in listings[:15]:
            try:
                # Title selector (Current class used in 2026)
                name_el = listing.locator('.qBF1Pd')
                name = name_el.inner_text() if name_el.count() > 0 else "Unknown"
                
                # Logic: Is the website button missing?
                # The authority data-item-id is the global marker for a website link
                has_website = listing.locator('a[data-item-id="authority"]').count() > 0
                
                if not has_website:
                    # Look for phone number text
                    phone = "N/A"
                    phone_el = listing.locator('span.Us79be').first
                    if phone_el.count() > 0:
                        phone = phone_el.inner_text()

                    leads.append({"Name": name, "Phone": phone})
                    print(f"🎯 Target Found: {name}")
            except:
                continue

        # Write to CSV
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        print(f"Scrape finished. {len(leads)} leads saved.")
        browser.close()

if __name__ == "__main__":
    hunt_leads()
