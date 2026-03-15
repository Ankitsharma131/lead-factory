import csv
import os
import re

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text).strip()
    return re.sub(r'[-\s]+', '-', text)

def generate_outreach():
    csv_file = 'leads.csv'
    github_base_url = "https://Ankitsharma131.github.io/lead-factory/"
    
    # We will save a formatted text for the shell script to read
    output_file = 'tg_messages.txt'

    if not os.path.exists(csv_file): return

    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with open(output_file, 'w', encoding='utf-8') as out:
            for row in reader:
                slug = slugify(row['Name'])
                demo_url = f"{github_base_url}{slug}.html"
                
                # Format for WhatsApp
                clean_phone = "".join(filter(str.isdigit, row['Phone']))
                if not clean_phone.startswith("91") and len(clean_phone) == 10:
                    clean_phone = "91" + clean_phone
                
                # The "Ready-to-Forward" Pitch
                tg_pitch = (
                    f"🏢 *{row['Name']}*\n"
                    f"📞 Contact: {row['Phone']}\n"
                    f"📍 Location: {row['Address']}\n\n"
                    f"*Your Pitch:*\n"
                    f"Hi {row['Name']}, I built a modern digital concept for your office at {row['Address']}. Check it out here: {demo_url}\n\n"
                    f"👉 [Click to WhatsApp](https://wa.me/{clean_phone}?text=Hi%20{row['Name'].replace(' ', '%20')},%20I%20built%20this%20for%20you:%20{demo_url})"
                )
                # Using a unique separator for the shell script
                out.write(tg_pitch + "---END---")

if __name__ == "__main__":
    generate_outreach()
