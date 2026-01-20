import os
import time
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ---- TEMP TEST (to confirm workflow runs) ----
send("🟢 CREX Alert system is LIVE.\nWaiting for 2nd innings win probability ≥ 70%")
