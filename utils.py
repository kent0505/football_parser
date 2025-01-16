from datetime import datetime, timedelta

import re
import os

base:        str = os.getenv("BASE", "")
url:         str = base + "/fixtures/_/date/"
goals_url:   str = base + "/match/_/gameId/"
stats_url:   str = base + "/matchstats/_/gameId/"
lineups_url: str = base + "/lineups/_/gameId/"
player_url:  str = os.getenv("PLAYER", "")
headers:     str = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}

def get_yesterday() -> str:
    date = datetime.now() - timedelta(days=1)
    # date = datetime.now()
    return date.strftime("%Y%m%d")
def extract_id(text) -> str:
    begin: str = "espncdn.com/combiner/i?img=/i/teamlogos"
    last: str = ".png&w=100&h=100"
    match = re.search(r"/id/(\d+)", text)
    if match:
        return f"https://a.{begin}/soccer/500/{match.group(1)}{last}"
    return f"https://secure.{begin}/default-team-logo-500{last}"
    # https://secure.espncdn.com/combiner/i?img=/i/teamlogos/default-team-logo-500.png&w=100&h=100
def extract_game_id(url: str) -> int | None:
    match = re.search(r"/gameId/(\d+)", url)
    return int(match.group(1)) if match else None
def get_coordinates(transform: str) -> str:
    return transform.replace("transform:translate(", "").replace("px", "").replace(")", "").replace(", ", "x")
