import csv
import os
import re
from jinja2 import Template

def slugify(text):
    """Converts business names to URL-friendly filenames."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

def build_demo_sites():
    output_dir = 'demos'
    template_file = 'template.html'
    csv_file = 'leads.csv'

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created directory: {output_dir}")

    # Check if files exist
    if not os.path.exists(template_file):
        print(f"❌ Error: {template_file} not found!")
        return
    if not os.path.exists(csv_file):
        print(f"❌ Error: {csv_file} not found! Run the Hunter first.")
        return

    # Load the template
    with open(template_file, 'r', encoding='utf-8') as f:
        html_template = f.read()
    
    jinja_template = Template(html_template)

    # Process leads
    count = 0
    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Generate a clean filename
            file_slug = slugify(row['Name'])
            filename = f"{file_slug}.html"
            
            # Inject data into template
            rendered_html = jinja_template.render(
                name=row['Name'],
                phone=row['Phone'],
                address=row['Address'],
                category=row['Category'],
                rating=row['Rating'],
                maps_link=row['MapsLink']
            )

            # Save the personalized site
            with open(os.path.join(output_dir, filename), "w", encoding='utf-8') as site_file:
                site_file.write(rendered_html)
            
            print(f"🏗️ Architect built: {filename}")
            count += 1

    print(f"\n✅ Phase 2 Complete: {count} personalized websites are ready in the '{output_dir}/' folder.")

if __name__ == "__main__":
    build_demo_sites()
