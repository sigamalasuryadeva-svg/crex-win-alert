import os
import math
import requests
from bs4 import BeautifulSoup
import re

# ---------- TELEGRAM SETTINGS ----------
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ---------- LOGISTIC REGRESSION COEFFICIENTS ----------
A  = -3.5
B1 = 0.45   # wickets remaining
B2 = 0.015  # balls remaining
B3 = -0.90  # required run rate

def win_probability(wkts, balls, rrr):
    z = A + (B1 * wkts) + (B2 * balls) + (B3 * rrr)
    return 1 / (1 + math.exp(-z))

send("🟢 Win Probability Engine Running (Debug Mode)")

# ---------- ALERT MEMORY ----------
alert_memory = set()

# ---------- GET LIVE MATCHES ----------
CRICBUZZ_LIVE_URL = "https://www.cricbuzz.com/cricket-match/live-scores"

try:
    r = requests.get(CRICBUZZ_LIVE_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    matches = soup.find_all("a", href=re.compile(r"/cricket-match/"))

    if not matches:
        send("ℹ️ No live matches found on Cricbuzz")
    else:
        for m in matches[:3]:  # limit to 3 matches
            match_link = "https://www.cricbuzz.com" + m['href']
            match_name = m.get_text(strip=True)

            r2 = requests.get(match_link)
            soup2 = BeautifulSoup(r2.text, "html.parser")
            text = soup2.get_text().lower()

            # Only 2nd innings
            if "2nd innings" not in text:
                print(f"Skipping {match_name} — no 2nd innings found")
                continue

            # ---------- EXTRACT TEAM NAMES ----------
            teams = soup2.find_all("div", class_="cb-nav-bar-title")
            if len(teams) >= 2:
                team1 = teams[0].get_text(strip=True)
                team2 = teams[1].get_text(strip=True)
            else:
                team1 = "TEAM1"
                team2 = "TEAM2"

            # ---------- EXTRACT SCORE ----------
            score_match = re.search(r'(\d+)[-/](\d+)\s*\((\d+\.?\d*)\s*ov\)', text)
            target_match = re.search(r'target\s+(\d+)', text)

            if score_match and target_match:
                runs_scored = int(score_match.group(1))
                wickets_fallen = int(score_match.group(2))
                overs_played = float(score_match.group(3))
                balls_played = int(overs_played * 6)

                target = int(target_match.group(1))
                runs_remaining = target - runs_scored

                # Detect balls per innings
                total_balls = 20*6 if target <= 250 else 50*6
                balls_remaining = max(0, total_balls - balls_played)
                wickets_remaining = 10 - wickets_fallen
                rrr = (runs_remaining / balls_remaining) * 6 if balls_remaining > 0 else 999

                p = win_probability(wickets_remaining, balls_remaining, rrr)
                percent = int(p * 100)

                # ---------- DEBUG PRINT ----------
                print(f"{match_name} | {team1} vs {team2} | Runs:{runs_scored}/{wickets_fallen} | Balls left:{balls_remaining} | RRR:{rrr:.2f} | P(win):{percent}%")

                # ---------- SEND ALERTS ----------
                thresholds = [50, 70, 80, 85]  # added 50% for testing
                for t in thresholds:
                    alert_id = f"{match_name}_{t}"
                    if percent >= t and alert_id not in alert_memory:
                        alert_memory.add(alert_id)
                        send(f"{match_name}\n{team1} – {percent}% VS {team2} – {100 - percent}%")

except Exception as e:
    send(f"❌ Error fetching live matches: {str(e)}")
