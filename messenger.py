import csv
import os
import re

def slugify(text):
    # Standard slugify for GitHub Pages URLs
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text).strip()
    return re.sub(r'[-\s]+', '-', text)

def generate_outreach():
    csv_file = 'leads.csv'
    # REPLACE with your actual GitHub username and repo name
    github_base_url = "https://Ankitsharma131.github.io/lead-factory/"
    output_file = 'tg_messages.txt'

    if not os.path.exists(csv_file):
        print("❌ leads.csv not found!")
        return

    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with open(output_file, 'w', encoding='utf-8') as out:
            count = 0
            for row in reader:
                slug = slugify(row['Name'])
                demo_url = f"{github_base_url}{slug}.html"
                
                # Clean phone for WhatsApp Link
                clean_phone = "".join(filter(str.isdigit, row['Phone']))
                if not clean_phone.startswith("91") and len(clean_phone) == 10:
                    clean_phone = "91" + clean_phone
                
                # Plain Text Message (Avoids Telegram Markdown Errors)
                msg = (
                    f"🏢 BUSINESS: {row['Name']}\n"
                    f"📞 PHONE: {row['Phone']}\n"
                    f"📍 LOC: {row['Address']}\n"
                    f"⭐ RATING: {row['Rating']}\n\n"
                    f"PITCH: Hi {row['Name']}, I built this demo for you: {demo_url}\n\n"
                    f"WHATSAPP: https://wa.me/{clean_phone}?text=Hi"
                )
                
                # Write message followed by the unique separator
                out.write(msg + "|||")
                count += 1
    
    print(f"✅ Generated {count} pitches in {output_file}")

if __name__ == "__main__":
    generate_outreach()
