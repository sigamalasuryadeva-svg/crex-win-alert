driver.get("https://crex.com/live-matches")
time.sleep(5)  # wait for JS to load

matches = driver.find_elements(By.CSS_SELECTOR, "div.match-card")

for match in matches:
    # Read league and teams
    league = match.find_element(By.CSS_SELECTOR, "div.match-league").text
    teams = match.find_elements(By.CSS_SELECTOR, "div.team-name")
    team1 = teams[0].text
    team2 = teams[1].text

    # Only second innings
    inning_text = match.find_element(By.CSS_SELECTOR, "div.inning-info").text
    if "2nd" not in inning_text:
        continue

    # Read exact probabilities
    wp1 = int(match.find_element(By.CSS_SELECTOR, "div.win-prob[data-team='1']").get_attribute("data-prob"))
    wp2 = int(match.find_element(By.CSS_SELECTOR, "div.win-prob[data-team='2']").get_attribute("data-prob"))

    # Send Telegram alert if thresholds crossed
