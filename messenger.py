import csv
import os
import re
import requests
import time

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text).strip()
    return re.sub(r'[-\s]+', '-', text)

def send_to_telegram(message):
    token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error sending to TG: {e}")

def generate_outreach():
    csv_file = 'leads.csv'
    github_base_url = "https://Ankitsharma131.github.io/lead-factory/"

    if not os.path.exists(csv_file):
        print("No leads.csv found.")
        return

    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            slug = slugify(row['Name'])
            demo_url = f"{github_base_url}{slug}.html"
            
            clean_phone = "".join(filter(str.isdigit, row['Phone']))
            if not clean_phone.startswith("91") and len(clean_phone) == 10:
                clean_phone = "91" + clean_phone
            
            # Create the message
            msg = (
                f"🏢 BUSINESS: {row['Name']}\n"
                f"📞 PHONE: {row['Phone']}\n"
                f"📍 LOC: {row['Address']}\n\n"
                f"PITCH: Hi {row['Name']}, I built this demo for you: {demo_url}\n\n"
                f"WHATSAPP: https://wa.me/{clean_phone}?text=Hi"
            )
            
            print(f"📤 Pushing {row['Name']} to Telegram...")
            send_to_telegram(msg)
            time.sleep(2) # Prevent spam block

if __name__ == "__main__":
    generate_outreach()
