import os
import csv
from playwright.sync_api import sync_playwright

def hunt_leads():
    # We use a specific search query from an environment variable or default
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    
    with sync_playwright() as p:
        # Launching headless for GitHub Actions
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        page = context.new_page()
        
        # Go to Google Maps search
        search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        page.goto(search_url)
        page.wait_for_timeout(5000)

        leads = []
        
        # Scroll logic for the sidebar
        for _ in range(3):
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(2000)

        # Selector for the business cards
        # Google Maps often uses 'div[role="article"]' or specific class markers
        listings = page.locator('div[role="article"]').all()

        for listing in listings[:10]: # Let's start with top 10 leads
            try:
                listing.click()
                page.wait_for_timeout(2000)

                # Check if Website button exists
                # 'authority' is the data-item-id for the website link in Gmaps
                has_website = page.locator('a[data-item-id="authority"]').count() > 0
                
                if not has_website:
                    name = page.locator('h1').first.inner_text()
                    # Extract phone via text search since IDs can shift
                    phone_loc = page.get_by_label(f"Phone:").first
                    phone = phone_loc.inner_text() if phone_loc.is_visible() else "No Phone"
                    
                    leads.append({"Name": name, "Phone": phone})
            except:
                continue

        # Save results
        with open('leads.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        browser.close()

if __name__ == "__main__":
    hunt_leads()
