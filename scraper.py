for listing in listings[:15]:
            try:
                name = listing.get_attribute("aria-label")
                if not name: continue
                
                # --- IMPROVED WEBSITE CHECK ---
                # 1. Check for the 'Globe' icon/authority link
                has_authority = listing.locator('a[data-item-id="authority"]').count() > 0
                
                # 2. Check for any text ending in .com, .in, .net, or .org in the card
                # Google often displays the website URL directly in the sub-text
                card_text = listing.inner_text().lower()
                has_url_text = any(ext in card_text for ext in ['.com', '.in', '.org', '.net', '.co'])

                # ONLY proceed if both checks fail (meaning NO website found)
                if not has_authority and not has_url_text:
                    # Click to get the phone number
                    listing.click()
                    time.sleep(2)
                    
                    phone = "N/A"
                    phone_el = page.locator('button[data-item-id^="phone:tel"]').first
                    if phone_el.is_visible():
                        phone = phone_el.get_attribute("data-item-id").replace("phone:tel:", "")

                    leads.append({"Name": name, "Phone": phone})
                    print(f"🎯 Real Lead (No Website): {name}")
                    page.keyboard.press("Escape")
                else:
                    print(f"⏩ Skipping {name} (Has Website)")
            except:
                continue
