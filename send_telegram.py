import os
import requests
import time

def send_messages():
    token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    file_path = 'tg_messages.txt'

    if not os.path.exists(file_path):
        print("⚠️ tg_messages.txt not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Split by the unique separator we defined in messenger.py
        messages = content.split("|||")

    for msg in messages:
        msg = msg.strip()
        if not msg:
            continue
            
        print(f"🚀 Sending: {msg.splitlines()[0]}") # Log the first line (Business Name)
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": msg,
            "disable_web_page_preview": False
        }
        
        try:
            response = requests.post(url, data=payload)
            if response.status_code != 200:
                print(f"❌ Failed to send. Error: {response.text}")
            time.sleep(1.5) # Avoid rate limiting
        except Exception as e:
            print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    send_messages()
