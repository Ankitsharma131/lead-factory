import os
import time
import csv
from playwright.sync_api import sync_playwright
from docx import Document

def create_status_doc(results, summary):
    doc = Document()
    doc.add_heading('Kolkata Lead Hunter: Daily Audit', 0)
    doc.add_heading('Summary', level=1)
    doc.add_paragraph(f"Total Listings Found: {summary['total']}")
    doc.add_paragraph(f"New Leads Added: {summary['added']}")
    doc.add_paragraph(f"Skipped (Known/Has Site): {summary['skipped']}")
    
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Company Name'
    hdr_cells[1].text = 'Status'
    hdr_cells[2].text = 'Reason'
    for item in results:
        row_cells = table.add_row().cells
        row_cells[0].text = item['name']
        row_cells[1].text = item['status']
        row_cells[2].text = item['reason']
    doc.save('status_report.docx')

def hunt_leads():
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/@22.5726,88.3639,13z"
    
    # --- HISTORY LOGIC ---
    history_file = 'history.txt'
    if not os.path.exists(history_file):
        open(history_file, 'w').close()
    with open(history_file, 'r') as f:
        seen_names = set(line.strip() for line in f)

    processing_log = []
    stats = {"total": 0, "added": 0, "skipped": 0}
    leads_for_csv = []
    new_seen = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        page.goto(search_url)
        page.wait_for_selector('div[role="article"]', timeout=15000)

        # Infinite Scroll
        last_count = 0
        while True:
            page.mouse.wheel(0, 8000)
            time.sleep(3)
            current_count = page.locator('div[role="article"]').count()
            if current_count == last_count or current_count > 150: break
            last_count = current_count

        listings = page.locator('div[role="article"]').all()
        
        for listing in listings:
            stats["total"] += 1
            name = listing.get_attribute("aria-label") or "Unknown"
            
            # Skip if already in history
            if name in seen_names:
                processing_log.append({"name": name, "status": "SKIPPED", "reason": "Already processed in a previous run."})
                stats["skipped"] += 1
                continue

            # Check website
            if listing.locator('a[data-item-id="authority"]').count() > 0:
                processing_log.append({"name": name, "status": "SKIPPED", "reason": "Has website."})
                stats["skipped"] += 1
                new_seen.append(name)
                continue

            # Deep check sidebar
            listing.click()
            time.sleep(1.5)
            if page.get_by_text("Add website").is_visible():
                phone = "N/A"
                phone_el = page.locator('button[data-item-id^="phone:tel"]').first
                if phone_el.is_visible():
                    phone = phone_el.get_attribute("data-item-id").replace("phone:tel:", "")
                
                processing_log.append({"name": name, "status": "ADDED", "reason": "Target lead found."})
                leads_for_csv.append({"Name": name, "Phone": phone})
                stats["added"] += 1
            else:
                processing_log.append({"name": name, "status": "SKIPPED", "reason": "No 'Add website' link."})
                stats["skipped"] += 1
            
            new_seen.append(name)
            page.keyboard.press("Escape")

        # Update History File
        with open(history_file, 'a') as f:
            for n in new_seen:
                f.write(n + '\n')

        create_status_doc(processing_log, stats)
        browser.close()

if __name__ == "__main__":
    hunt_leads()
