from fastapi  import APIRouter, HTTPException
from pydantic import BaseModel
from bs4      import BeautifulSoup
from utils    import *

import database

import aiohttp
import logging

router = APIRouter()

class Player(BaseModel):
    pid: int = 5178
    name: str = "Mohamed Salah"
    position: str = "Forward"
    team: str = "Liverpool"
    number: int = 11

@router.post("/player")
async def add_player(body: Player):
    player = await database.get_player(body.pid)
    if player: 
        raise HTTPException(409, "player already exists")
    await database.add_player(
        body.pid, 
        body.name,
        body.position,
        body.team,
        body.number,
    )
    return {"message": "player added"}

@router.delete("/player/{pid}")
async def delete_player(pid: int):
    player = await database.get_player(pid)
    if player:
        await database.delete_player(pid)
        return {"message": "player deleted"}
    raise HTTPException(404, "player not found")


@router.get("/players")
async def get_players():
    players = []
    rows = await database.get_players()
    for row in rows:
        players.append({
            "id": row[0],
            "pid": row[1],
            "name": row[2],
            "position": row[3],
            "team": row[4],
            "number": row[5],
        })
    return {"players": players}

@router.get("/player/{id}")
async def get_player(id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{player_url}{id}/player/stats", headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                try:
                    print(f"{player_url}{id}/player/stats")
                    # print(html)
                    # data = soup.find_all("tbody", class_="Table__TBODY")
                    # for tbody in data:
                    #     rows = tbody.find_all("tr", class_="Table__TR Table__TR--sm Table__even")
                    #     for row in rows:
                    #         stadium = row.find("td", class_="venue__col Table__TD")
                    #         team1 = row.find("td", class_="events__col Table__TD")
                    #         team2 = row.find("td", class_="colspan__col Table__TD")
                    #         title1 = team1.find("span", class_="Table__Team away")
                    #         title2 = team2.find("span", class_="Table__Team")
                    #         logo1 = title1.find("a", class_="AnchorLink")
                    #         logo2 = title2.find("a", class_="AnchorLink")
                    #         score = team2.find("a", class_="AnchorLink at")
                    #         id = extract_game_id(score.get("href"))
                    #         if id:
                    #             fixtures.append({
                    #                 "id": id,
                    #                 "score": score.text.strip(),
                    #                 "stadium": stadium.text.strip(),
                    #                 "home": {
                    #                     "title": title1.text.strip(),
                    #                     "logo": extract_id(logo1.get("href")),
                    #                 },
                    #                 "away": {
                    #                     "title": title2.text.strip(),
                    #                     "logo": extract_id(logo2.get("href")),
                    #                 },
                    #             })
                except Exception as e:
                    logging.error(e)
            return {
                "status": response.status,
                "player": {
                    "name": "Erling Haaland",
                    "number": "Erling Haaland",
                    "team": "Manchester City", 
                    "position": "Forward",
                    "age": "24", # overview section
                    "height": "194cm", # overview section
                    "yc": 8,
                    "rc": 0,
                    "fouls": 63,
                    "shots": 325,
                    "goals": 79,
                    "passes": 1088,
                    "tackles": 15,
                },
            }
