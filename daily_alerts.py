import os
import requests

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise Exception("❌ Telegram bot token or chat ID missing")

message = "✅ Test Alert! Telegram bot is working."

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
response = requests.post(url, json={"chat_id": CHAT_ID, "text": message})

print(response.text)
