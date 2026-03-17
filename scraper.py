import os
import time
import csv
import re
from playwright.sync_api import sync_playwright
# Updated import to fix the 'stealth_sync' error
from playwright_stealth import stealth_page

# 1. GET DYNAMIC INPUT FROM GITHUB ACTIONS
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
        # Launching with standard args for better stability in GitHub Actions
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Apply stealth to the page to avoid detection
        stealth_page(page)

        # Navigate to Google Maps search
        page.goto(f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}")
        page.wait_for_timeout(5000)

        # Scroll to load businesses
        for _ in range(3):
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(2000)

        # Locate business articles
        results = page.query_selector_all('div[role="article"]')
        
        for res in results:
            try:
                name = res.get_attribute('aria-label')
                if not name or name in history:
                    continue

                # Get address info
                address_element = res.query_selector('.fontBodyMedium')
                address = address_element.inner_text().split('·')[-1].strip() if address_element else "Address Unknown"
                
                # Get Rating
                rating_element = res.query_selector('span[aria-label*="stars"]')
                rating = rating_element.get_attribute('aria-label').split()[0] if rating_element else "0.0"

                # Check if a website exists (if the website icon is missing, they need us!)
                website_btn = res.query_selector('a[aria-label*="website"]')
                
                if not website_btn:
                    lead_data = {
                        "Name": name,
                        "Phone": "See Maps Link", 
                        "Address": address,
                        "Category": search_query.split(' in ')[0],
                        "Rating": rating,
                        "MapsLink": f"https://www.google.com/maps/search/{name.replace(' ', '+')}"
                    }
                    
                    leads.append(lead_data)
                    save_history(name)
                    print(f"✅ Target Found: {name}")

                if len(leads) >= 15: # Safety limit for Delhi run
                    break
                    
            except Exception as e:
                continue

        browser.close()

    # Save findings
    if leads:
        keys = leads[0].keys()
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(leads)
        print(f"📊 Saved {len(leads)} leads to leads.csv")
    else:
        print("⚠️ No NEW leads without websites found in this area.")

if __name__ == "__main__":
    run_scraper()
