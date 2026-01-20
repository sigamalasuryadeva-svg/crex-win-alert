import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CREX_URL = "https://crex.com/live-matches"

thresholds = [70, 80, 85]
sent_alerts = {}

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

while True:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(CREX_URL)
    time.sleep(5)  # wait page to load

    matches = driver.find_elements(By.CSS_SELECTOR, "div.match-card")

    for match in matches:
        try:
            league = match.find_element(By.CSS_SELECTOR, "div.match-league").text
            teams = match.find_elements(By.CSS_SELECTOR, "div.team-name")
            team1 = teams[0].text
            team2 = teams[1].text

            inning_text = match.find_element(By.CSS_SELECTOR, "div.inning-info").text
            if "2nd" not in inning_text:
                continue

            # Read exact probabilities from CREX
            wp1 = int(match.find_element(By.CSS_SELECTOR, "div.win-prob[data-team='1']").get_attribute("data-prob"))
            wp2 = int(match.find_element(By.CSS_SELECTOR, "div.win-prob[data-team='2']").get_attribute("data-prob"))

            match_id = f"{team1}-{team2}"
            if match_id not in sent_alerts:
                sent_alerts[match_id] = []

            for th in thresholds:
                if wp1 >= th and th not in sent_alerts[match_id]:
                    message = f"{league} Match {team1} VS {team2} , {team1}-{wp1}% VS {team2}-{wp2}%"
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                                  json={"chat_id": CHAT_ID, "text": message})
                    sent_alerts[match_id].append(th)

        except Exception as e:
            print("Error parsing match:", e)

    driver.quit()
    time.sleep(30)  # check again in 30 seconds
