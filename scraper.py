import os
import csv
import time
from playwright.sync_api import sync_playwright

def hunt_leads():
    # 1. Search query
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    
    # 2. Coordinates for Kolkata (Latitude 22.57, Longitude 88.36)
    # The '@...' part of the URL tells Google Maps EXACTLY where to center the camera.
    kolkata_center = "@22.5726,88.3639,13z"
    search_url = f"https://www.google.com/maps/place/McDonald\\'s/data=!4m7!3m6!1s0x47e66fea26bafdc7:0x21ea7aaf1fb2b3e3!8m2!3d48.8729997!4d2.2991604!16s%2Fg%2F1hd_88rdh!19sChIJx_26Jupv5kcR47OyH6966iE?authuser=0&hl=en&rclk=1{query.replace(' ', '+')}/{kolkata_center}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"🕵️ Hunter focusing on Kolkata...")
        page.goto(search_url)
        time.sleep(5)

        leads = []
        try:
            # 3. Improved Scroll - ensures the list actually populates
            scrollable = page.locator('div[role="feed"]')
            for _ in range(3):
                page.mouse.wheel(0, 3000)
                time.sleep(2)

            # 4. Extract listings
            listings = page.locator('div[role="article"]').all()
            print(f"📋 Found {len(listings)} businesses. Checking for website-less leads...")

            for listing in listings[:15]:
                name = listing.get_attribute("aria-label")
                if not name: continue
                
                # Check for website
                has_website = listing.locator('a[data-item-id="authority"]').count() > 0
                
                if not has_website:
                    # 5. Get Phone Number (Clicking to open sidebar)
                    listing.click()
                    time.sleep(2) # Give the detail pane time to slide out
                    
                    phone = "N/A"
                    # The button for the phone usually has a specific tel link
                    phone_el = page.locator('button[data-item-id^="phone:tel"]').first
                    if phone_el.is_visible():
                        phone = phone_el.get_attribute("data-item-id").replace("phone:tel:", "")

                    leads.append({"Name": name, "Phone": phone})
                    print(f"🎯 Target Found: {name} | Phone: {phone}")
                    
                    # Close the detail pane for the next search
                    page.keyboard.press("Escape")

        except Exception as e:
            print(f"❌ Error: {e}")

        # 6. Save results
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
            writer.writeheader()
            writer.writerows(leads)
        
        print(f"✅ Success! Saved {len(leads)} Kolkata targets.")
        browser.close()

if __name__ == "__main__":
    hunt_leads()
