import os
import requests

# Get token and chat ID from GitHub secrets
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise Exception("❌ Telegram bot token or chat ID missing")

# Message to send
message = "✅ Test Alert! Telegram bot is working."

# Telegram API URL
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# Send the message
response = requests.post(url, json={"chat_id": CHAT_ID, "text": message})

# Print response in GitHub Actions logs
print(response.text)
