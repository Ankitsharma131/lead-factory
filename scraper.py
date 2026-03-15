# --- IMPROVED DEEP SCROLL BLOCK ---
        print("🔄 Identifying results panel for deep scroll...")
        
        # This selector targets the actual scrollable list container in 2026
        results_panel_selector = '.m67qEc' 
        
        last_count = 0
        scroll_attempts = 0
        
        while scroll_attempts < 20: # Safety cap to prevent infinite loops
            # 1. Locate the scrollable panel
            panel = page.locator('div[role="feed"]')
            
            # 2. Hover over the panel so the scroll 'lands' in the right place
            panel.hover()
            
            # 3. Scroll down heavily
            page.mouse.wheel(0, 10000)
            
            # 4. Wait for the 'loading' spinner to finish
            time.sleep(4) 
            
            current_count = page.locator('div[role="article"]').count()
            print(f"📊 Scroll attempt {scroll_attempts + 1}: Found {current_count} listings...")
            
            if current_count == last_count:
                # Double check: try one more tiny scroll in case it's just slow
                page.mouse.wheel(0, 2000)
                time.sleep(2)
                if page.locator('div[role="article"]').count() == last_count:
                    print("🏁 Reached the end of the 120+ results.")
                    break
            
            last_count = current_count
            scroll_attempts += 1
        # --- END SCROLL ---
