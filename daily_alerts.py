import os
import math
import requests
import time

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ---- Logistic regression coefficients ----
A  = -3.5
B1 = 0.45   # wickets remaining
B2 = 0.015  # balls remaining
B3 = -0.90  # required run rate

def win_probability(wkts, balls, rrr):
    z = A + (B1 * wkts) + (B2 * balls) + (B3 * rrr)
    return 1 / (1 + math.exp(-z))

send("🟢 Win Probability Engine Running")

# ------------------------------------------------------------------
# TEMP DEMO INPUT (this simulates a real 2nd innings situation)
# Later this will be replaced by live score parsing
# ------------------------------------------------------------------

match_name = "BPL: TEAM A vs TEAM B"
wickets_remaining = 8
balls_remaining = 48
required_run_rate = 6.2

p = win_probability(wickets_remaining, balls_remaining, required_run_rate)
percent = int(p * 100)

if percent >= 70:
    send(
        f"{match_name}\n"
        f"TEAM A – {percent}% VS TEAM B – {100 - percent}%"
    )
