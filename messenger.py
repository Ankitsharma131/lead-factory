name: Lead Factory Master Pipeline

on:
  schedule:
    - cron: '30 3 * * *' # Runs daily at 9:00 AM IST
  workflow_dispatch: # Allows manual trigger

permissions:
  contents: write
  pages: write
  id-token: write

jobs:
  factory-run:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Python Environment
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install System Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install playwright playwright-stealth python-docx jinja2
          playwright install chromium

      - name: 🔥 Phase 1: The Hunt (Scraper)
        env:
          SEARCH_QUERY: "HR Consultancy in Kolkata"
        run: python scraper.py

      - name: 🏗️ Phase 2: The Architect (Site Builder)
        run: python architect.py

      - name: ✉️ Phase 3: The Messenger (Pitch Generator)
        run: python messenger.py

      - name: 💾 Commit State (History Update)
        run: |
          git config --global user.name "LeadBot-Master"
          git config --global user.email "bot@github.com"
          git add history.txt
          # Only commit if history.txt was actually updated
          git commit -m "chore: update leads history [skip ci]" || echo "No new history to save"
          git push

      - name: 🌐 Upload Demos to GitHub Pages
        uses: actions/upload-pages-artifact@v3
        with:
          path: './demos'

      - name: 🚀 Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4

      - name: 📱 Push Individual Leads to Telegram
        if: always()
        env:
          TG_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TG_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          if [ -f tg_messages.txt ]; then
            echo "✅ tg_messages.txt found. Starting Telegram push..."
            
            # Use awk to split by the ||| separator and loop through messages
            awk 'BEGIN {RS="|||"} {print}' tg_messages.txt | while read -r message; do
              if [ ! -z "$message" ]; then
                echo "Pushing lead to Telegram..."
                curl -s -X POST "https://api.telegram.org/bot$TG_BOT_TOKEN/sendMessage" \
                     --data-urlencode "chat_id=$TG_CHAT_ID" \
                     --data-urlencode "text=$message" \
                     --data-urlencode "disable_web_page_preview=false"
                
                # Prevent Telegram rate limiting (Max 30 msg/sec, we stay safe with 2s)
                sleep 2 
              fi
            done
          else
            echo "⚠️ No new leads found. tg_messages.txt is missing."
          fi

      - name: 📊 Backup Data Files
        if: always()
        run: |
          if [ -f leads.csv ]; then
            curl -s -F chat_id=${{ secrets.TELEGRAM_CHAT_ID }} \
                 -F document=@leads.csv \
                 -F caption="📊 Daily Master Backup (CSV)" \
                 https://api.telegram.org/bot${{ secrets.TELEGRAM_BOT_TOKEN }}/sendDocument
          fi
