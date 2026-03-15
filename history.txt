import csv
import os
import re
from jinja2 import Template

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

def get_image_for_category(category):
    cat = category.lower()
    # Unsplash Image IDs
    images = {
        "hr": "1521731978142-2e67a34ad7b1",
        "consult": "1454165804606-c3d5fbc56fe5",
        "tech": "1519389950473-47ba0277781c",
        "office": "1497366216548-37526070297c"
    }
    if "hr" in cat or "recruit" in cat: return images["hr"]
    if "consult" in cat: return images["consult"]
    if "tech" in cat or "it" in cat: return images["tech"]
    return images["office"]

def build_demo_sites():
    output_dir = 'demos'
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    with open('template.html', 'r', encoding='utf-8') as f:
        jinja_template = Template(f.read())

    with open('leads.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            file_slug = slugify(row['Name'])
            img_id = get_image_for_category(row['Category'])
            
            rendered_html = jinja_template.render(
                name=row['Name'],
                phone=row['Phone'],
                address=row['Address'],
                category=row['Category'],
                rating=row['Rating'],
                maps_link=row['MapsLink'],
                image_id=img_id # New variable for Unsplash
            )

            with open(os.path.join(output_dir, f"{file_slug}.html"), "w", encoding='utf-8') as sf:
                sf.write(rendered_html)
            print(f"✨ Enhanced build: {file_slug}.html")

if __name__ == "__main__":
    build_demo_sites()
