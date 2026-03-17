import os
import time
import csv
import re
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# 1. GET DYNAMIC INPUT FROM GITHUB ACTIONS
# If running locally, it defaults to 'HR Consultancy in Delhi'
search_query = os.getenv("SEARCH_QUERY", "HR Consultancy in Delhi")

def slugify(text):
    return re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', text.lower()).strip())

def load_history():
    if os.path.exists('history.txt'):
        with open('history.txt', 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f)
    return set()

def save_history(name):
    with open('history.txt', 'a', encoding='utf-8') as f:
        f.write(f"{name}\n")

def run_scraper():
    history = load_history()
    leads = []
    
    print(f"🚀 Starting Hunt for: {search_query}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        stealth_sync(page)

        # Go to Google Maps
        page.goto(f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}")
        page.wait_for_timeout(5000)

        # Scroll to load leads
        for _ in range(5):
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(2000)

        # Find all business results
        results = page.query_selector_all('div[role="article"]')
        
        for res in results:
            try:
                name = res.get_attribute('aria-label')
                if not name or name in history:
                    continue

                # Basic Filter: Check if Website button exists
                # In a real scenario, you'd click into the lead to verify 'no website'
                # For this version, we assume leads found in this list are targets
                
                # Scrape visible data
                address_element = res.query_selector('text=Kolkata|Delhi|Sector|Street') # Dynamic detection
                address = address_element.inner_text() if address_element else "Address not listed"
                
                rating_element = res.query_selector('span[aria-label*="stars"]')
                rating = rating_element.get_attribute('aria-label').split()[0] if rating_element else "No Rating"

                # If lead is new, add to our list
                lead_data = {
                    "Name": name,
                    "Phone": "Extracting...", # Placeholder for deeper click-thru logic
                    "Address": address,
                    "Category": search_query.split(' in ')[0],
                    "Rating": rating,
                    "MapsLink": "https://www.google.com/maps/search/" + name.replace(" ", "+")
                }
                
                leads.append(lead_data)
                save_history(name)
                print(f"✅ Found New Lead: {name}")

                if len(leads) >= 20: # Limit per run to stay under GitHub's time limits
                    break
                    
            except Exception as e:
                continue

        browser.close()

    # Save to CSV for the Architect and Messenger to use
    if leads:
        keys = leads[0].keys()
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(leads)
        print(f"📊 Saved {len(leads)} leads to leads.csv")
    else:
        print("⚠️ No new leads found today.")

if __name__ == "__main__":
    run_scraper()
