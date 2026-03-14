for listing in listings[:15]:
            try:
                name = listing.get_attribute("aria-label")
                if not name: continue
                
                # --- NEW DEEP FILTER ---
                # 1. Check for the "Website" globe icon button specifically
                # 2. Also check if the text "Website" appears anywhere in the card
                website_btn = listing.get_by_role("link", name="Website")
                has_website_icon = listing.locator('a[data-item-id="authority"]').count() > 0
                
                # If either the text 'Website' or the Icon exists, they have a site!
                if website_btn.count() > 0 or has_website_icon:
                    print(f"⏭️ Skipping {name} (Has Website)")
                    continue 

                # If we reached here, they truly have no website button
                phone = "N/A"
                phone_el = listing.locator('span.Us79be').first
                if phone_el.count() > 0:
                    phone = phone_el.inner_text()

                leads.append({"Name": name, "Phone": phone})
                print(f"🎯 Target Found: {name}")

            except Exception:
                continue
