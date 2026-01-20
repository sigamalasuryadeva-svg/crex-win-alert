import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

send("🟢 CREX Monitor started\nChecking live matches...")

# Chrome setup (headless)
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

try:
    driver.get("https://crex.com/live-matches")
    time.sleep(8)

    matches = driver.find_elements(By.CSS_SELECTOR, "a.match-card")

    if not matches:
        send("ℹ️ No live matches currently")
    else:
        for match in matches[:5]:  # limit for safety
            link = match.get_attribute("href")
            driver.get(link)
            time.sleep(8)

            page = driver.page_source.lower()

            if "2nd innings" not in page:
                continue

            # TEMP placeholder (real prob parsing next step)
            send("🟡 Live 2nd innings detected\nWaiting for probability logic")

finally:
    driver.quit()
