import os
import requests
import time

def send_leads():
    # GitHub automatically populates these from your Secrets
    token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    file_path = 'tg_messages.txt'

    if not os.path.exists(file_path):
        print("⚠️ No messages found in tg_messages.txt. Skipping...")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Splitting by the custom separator we used in messenger.py
        messages = content.split("|||")

    for msg in messages:
        msg = msg.strip()
        if not msg:
            continue
            
        print(f"📤 Attempting to send message for: {msg.splitlines()[0]}")
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": msg,
            "disable_web_page_preview": False
        }
        
        try:
            response = requests.post(url, data=payload, timeout=10)
            if response.status_code == 200:
                print("✅ Successfully sent.")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
            
            # Anti-spam delay
            time.sleep(2) 
        except Exception as e:
            print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    send_leads()
