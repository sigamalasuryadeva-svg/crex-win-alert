import os
import math
import requests
from bs4 import BeautifulSoup

# ---------- TELEGRAM SETTINGS ----------
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ---------- LOGISTIC REGRESSION ----------
A  = -3.5
B1 = 0.45   # wickets remaining
B2 = 0.015  # balls remaining
B3 = -0.90  # required run rate

def win_probability(wkts, balls, rrr):
    z = A + (B1 * wkts) + (B2 * balls) + (B3 * rrr)
    return 1 / (1 + math.exp(-z))

send("🟢 Win Probability Engine Running (Cricbuzz Live)")

# ---------- ALERT MEMORY ----------
alert_memory = set()

# ---------- GET LIVE MATCHES ----------
CRICBUZZ_LIVE_URL = "https://www.cricbuzz.com/cricket-match/live-scores"

try:
    r = requests.get(CRICBUZZ_LIVE_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    # find live matches links
    match_links = soup.find_all("a", {"class": "cb-lv-scrs-well"})
    if not match_links:
        send("ℹ️ No live matches found on Cricbuzz")
    else:
        for m in match_links[:3]:  # limit to first 3 matches
            link = "https://www.cricbuzz.com" + m['href']
            match_name = m.get_text(strip=True)

            # open match page
            r2 = requests.get(link)
            soup2 = BeautifulSoup(r2.text, "html.parser")

            # ---------- EXTRACT TEAM NAMES ----------
            teams = soup2.find_all("div", {"class": "cb-nav-bar-title"})
            if len(teams) >= 2:
                team1 = teams[0].get_text(strip=True)
                team2 = teams[1].get_text(strip=True)
            else:
                team1, team2 = "TEAM1", "TEAM2"

            # ---------- EXTRACT 2ND INNINGS SCORE ----------
            score_divs = soup2.find_all("div", {"class": "cb-col cb-col-50 cb-scrs-wrp"})
            second_innings_found = False
            for div in score_divs:
                text = div.get_text(strip=True)
                if "target" in text.lower() or "overs" in text.lower():
                    second_innings_found = True
                    # parse score like 90/3 (8.0 ov)
                    import re
                    score_match = re.search(r'(\d+)[-/](\d+)\s*\((\d+\.?\d*)\s*ov\)', text)
                    target_match = re.search(r'target\s+(\d+)', text, re.IGNORECASE)
                    if score_match and target_match:
                        runs_scored = int(score_match.group(1))
                        wickets_fallen = int(score_match.group(2))
                        overs_played = float(score_match.group(3))
                        balls_played = int(overs_played * 6)

                        target = int(target_match.group(1))
                        runs_remaining = target - runs_scored

                        # detect balls per innings (20 or 50)
                        total_balls = 20*6 if target <= 250 else 50*6
                        balls_remaining = max(0, total_balls - balls_played)
                        wickets_remaining = 10 - wickets_fallen
                        rrr = (runs_remaining / balls_remaining) * 6 if balls_remaining > 0 else 999

                        p = win_probability(wickets_remaining, balls_remaining, rrr)
                        percent = int(p * 100)

                        # ---------- SEND ALERTS ----------
                        thresholds = [70, 80, 85]
                        for t in thresholds:
                            alert_id = f"{match_name}_{t}"
                            if percent >= t and alert_id not in alert_memory:
                                alert_memory.add(alert_id)
                                send(f"{match_name}\n{team1} – {percent}% VS {team2} – {100 - percent}%")

            if not second_innings_found:
                print(f"No 2nd innings data found for {match_name}")

except Exception as e:
    send(f"❌ Error fetching live matches: {str(e)}")
