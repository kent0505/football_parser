from fastapi import APIRouter
from bs4     import BeautifulSoup
from utils   import *

import aiohttp
import logging

router = APIRouter()

@router.get("/fixtures")
async def get_fixtures():
    async with aiohttp.ClientSession() as session:
        yesterday = get_yesterday()
        async with session.get(url+yesterday, headers=headers) as response:
            fixtures = []
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                try:
                    data = soup.find_all("tbody", class_="Table__TBODY")
                    for tbody in data:
                        rows = tbody.find_all("tr", class_="Table__TR Table__TR--sm Table__even")
                        for row in rows:
                            stadium = row.find("td", class_="venue__col Table__TD")
                            team1 = row.find("td", class_="events__col Table__TD")
                            team2 = row.find("td", class_="colspan__col Table__TD")
                            title1 = team1.find("span", class_="Table__Team away")
                            title2 = team2.find("span", class_="Table__Team")
                            logo1 = title1.find("a", class_="AnchorLink")
                            logo2 = title2.find("a", class_="AnchorLink")
                            score = team2.find("a", class_="AnchorLink at")
                            id = extract_game_id(score.get("href"))
                            if id:
                                fixtures.append({
                                    "id": id,
                                    "score": score.text.strip(),
                                    "stadium": stadium.text.strip(),
                                    "home": {
                                        "title": title1.text.strip(),
                                        "logo": extract_id(logo1.get("href")),
                                    },
                                    "away": {
                                        "title": title2.text.strip(),
                                        "logo": extract_id(logo2.get("href")),
                                    },
                                })
                except Exception as e:
                    logging.error(e)
            return {
                "yesterday": yesterday,
                "status": response.status,
                "amount": len(fixtures),
                "fixtures": fixtures,
            }

@router.get("/goals/{id}")
async def get_goals(id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(goals_url+id, headers=headers) as response:
            goals = []
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                try:
                    divs = soup.find_all("div", class_="SoccerPerformers")
                    for div in divs:
                        uls = div.find_all("ul", class_="SoccerPerformers__Competitor__Info__GoalsList")
                        for ul in uls:
                            lis = ul.find_all("li", class_="SoccerPerformers__Competitor__Info__GoalsList__Item")
                            for li in lis:
                                player = li.find("strong", class_="Soccer__PlayerName").text.strip()
                                time = li.find("span", class_="GoalScore__Time").text.strip().replace("- ", "").replace("'", "")
                                if player and time:
                                    goals.append({
                                        "player": player,
                                        "time": time,
                                    })
                except Exception as e:
                    logging.error(e)
            return {
                "status": response.status,
                "goals": goals,
            }

@router.get("/stats/{id}")
async def get_stats(id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(stats_url+id, headers=headers) as response:
            stats = []
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                try:
                    possession = soup.find("div", class_="eZKkr")
                    titles = possession.find_all("div", class_="LOSQp")
                    for t in titles:
                        title = t.find("span", class_="OkRBU")
                        values = t.find_all("span", class_="bLeWt")
                        if len(values) == 2:
                            stats.append({
                                "title": title.text.strip(),
                                "team1": values[0].text.strip(),
                                "team2": values[1].text.strip(),
                            })
                except Exception as e:
                    logging.error(e)
            return {
                "status": response.status,
                "stats": stats,
            }

@router.get("/lineups/{id}")
async def get_lineups(id: str):
    async def extract_team_data(section):
        team = []
        formation = section.find("span", class_="LineUps__TabsHeader__Title").text.strip()
        field = section.find("ul", class_="TacticalFormation__Field")
        players = field.find_all("li", class_="TacticalFormation__Field__Player")
        for player in players:
            name = player.find("span", class_="TacticalFormation__Field__Player__Name").text.strip()
            number = player.find("div", class_="headshot-jerseyV2__player-number").text.strip()
            position = get_coordinates(player.get("style"))
            team.append({
                "name": name, 
                "number": number, 
                "position": position,
            })
        return {
            "formation": formation, 
            "players": team,
        }
    async with aiohttp.ClientSession() as session:
        async with session.get(lineups_url+id, headers=headers) as response:
            lineups = []
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                try:
                    both = soup.find("div", class_="LineUps__BothTeams")
                    sections = both.find_all("section", class_="Card")
                    if len(sections) == 2:
                        lineups = [await extract_team_data(section) for section in sections]
                except Exception as e:
                    logging.error(e)
            return {
                "status": response.status,
                "lineups": lineups,
            }