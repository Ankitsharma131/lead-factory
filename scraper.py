import os
import time
import csv
from playwright.sync_api import sync_playwright
from docx import Document
from docx.shared import Inches

def create_status_doc(results, summary):
    """Generates a professional Word document report."""
    doc = Document()
    doc.add_heading('Kolkata Lead Hunter: Daily Report', 0)
    
    # Add Summary Section
    doc.add_heading('Summary', level=1)
    doc.add_paragraph(f"Total Businesses Checked: {summary['total']}")
    doc.add_paragraph(f"Targets Added to Leads: {summary['added']}")
    doc.add_paragraph(f"Businesses Skipped: {summary['skipped']}")
    
    # Add Detailed Log Table
    doc.add_heading('Detailed Processing Log', level=1)
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Company Name'
    hdr_cells[1].text = 'Status'
    hdr_cells[2].text = 'Reason for Decision'
    
    for item in results:
        row_cells = table.add_row().cells
        row_cells[0].text = item['name']
        row_cells[1].text = item['status']
        row_cells[2].text = item['reason']
    
    doc.save('status_report.docx')
    print("✅ Status report saved as status_report.docx")

def hunt_leads():
    query = os.getenv("SEARCH_QUERY", "HR Consultancy in Kolkata")
    # Coordinate locked URL for Kolkata
    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/@22.5726,88.3639,13z"
    
    processing_log = []
    stats = {"total": 0, "added": 0, "skipped": 0}
    leads_for_csv = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print(f"🕵️ Starting search for: {query}")
        page.goto(search_url)
        
        try:
            page.wait_for_selector('div[role="article"]', timeout=15000)
            listings = page.locator('div[role="article"]').all()
            
            for listing in listings[:15]:
                stats["total"] += 1
                name = listing.get_attribute("aria-label") or "Unknown Business"
                
                # GATE 1: Check for website button in list
                website_btn = listing.locator('a[data-item-id="authority"]')
                
                if website_btn.count() > 0:
                    processing_log.append({"name": name, "status": "SKIPPED", "reason": "Already has a website link/button in Google Maps."})
                    stats["skipped"] += 1
                    continue

                # GATE 2: Deep check sidebar for "Add website"
                listing.click()
                time.sleep(2)
                
                if page.get_by_text("Add website").is_visible():
                    phone = "N/A"
                    phone_el = page.locator('button[data-item-id^="phone:tel"]').first
                    if phone_el.is_visible():
                        phone = phone_el.get_attribute("data-item-id").replace("phone:tel:", "")
                    
                    processing_log.append({"name": name, "status": "ADDED", "reason": "No website found and 'Add website' button is present."})
                    leads_for_csv.append({"Name": name, "Phone": phone})
                    stats["added"] += 1
                else:
                    processing_log.append({"name": name, "status": "SKIPPED", "reason": "No website button, but sidebar does not offer 'Add website' option."})
                    stats["skipped"] += 1
                
                page.keyboard.press("Escape")

        except Exception as e:
            print(f"❌ Error during scrape: {e}")

        # Save debug screenshot
        page.screenshot(path="debug_view.png")
        
        # Save CSV for Phase 2 use
        keys = leads_for_csv[0].keys() if leads_for_csv else ["Name", "Phone"]
        with open('leads.csv', 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(leads_for_csv)

        # Create the Word Document Report
        create_status_doc(processing_log, stats)
        browser.close()

if __name__ == "__main__":
    hunt_leads()
