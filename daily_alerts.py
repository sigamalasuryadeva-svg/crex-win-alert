import os
import requests
import time

# Telegram bot setup
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise Exception("❌ Telegram bot token or chat ID missing")

# Track alerts already sent to avoid duplicates
sent_alerts = {}

# Thresholds for alerts
thresholds = [70, 80, 85]

while True:
    try:
        # Fetch live matches from CREX
        # NOTE: Replace this URL with the real CREX API or scraper URL
        response = requests.get("https://api.crex.com/live-matches")  # Placeholder
        matches = response.json()  # List of matches

        for match in matches:
            match_id = match['match_id']
            league = match['league']
            team1 = match['team1']
            team2 = match['team2']
            inning = match['inning']
            wp1 = match['win_probability_team1']
            wp2 = match['win_probability_team2']

            # Only second innings
            if inning != 2:
                continue

            # Initialize alerts for this match
            if match_id not in sent_alerts:
                sent_alerts[match_id] = []

            # Send alerts for thresholds
            for th in thresholds:
                if th <= wp1 and th not in sent_alerts[match_id]:
                    message = f"{league} Match {team1} VS {team2} , {team1}-{int(wp1)}% VS {team2}-{int(wp2)}%"
                    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                    requests.post(url, json={"chat_id": CHAT_ID, "text": message})
                    sent_alerts[match_id].append(th)

        # Wait 30 seconds before checking again
        time.sleep(30)

    except Exception as e:
        print("Error:", e)
        time.sleep(30)
