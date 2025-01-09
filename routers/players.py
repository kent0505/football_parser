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

@router.get("/player/{pid}")
async def get_player(pid: int):
    player = await database.get_player(pid)
    if player:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{player_url}{pid}/player/stats", headers=headers) as response:
                logging.info(f"{player_url}{pid}/player/stats")
                stats = {}
                name = "?"
                position = "?"
                team = "?"
                number = "0"
                age = "0"
                height = "0"

                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "lxml")
                    try:
                        first_name = soup.find("div", class_="player-header__name-first").get_text(strip=True)
                        last_name = soup.find("div", class_="player-header__name-last").get_text(strip=True)
                        name = f"{first_name} {last_name}"
                        number = soup.find("div", class_="player-header__player-number player-header__player-number--large").text.strip()

                        cols = soup.find("section", class_="player-overview__side-widget").find_all("div", class_="player-overview__col")
                        age = cols[1].find("div", class_="player-overview__info").get_text(strip=True)
                        height = cols[2].find("div", class_="player-overview__info").get_text(strip=True)
                        team = cols[3].find("div", class_="player-overview__info").get_text(strip=True)
                        position = cols[4].find("div", class_="player-overview__info").get_text(strip=True)

                        ul = soup.find("ul", class_="player-stats__stats-wrapper")
                        for li in ul.find_all("li", class_="player-stats__stat"):
                            for div in li.find_all("div", class_="player-stats__stat-value"):
                                title = div.find(text=True, recursive=False).strip()
                                value = div.find("span").get_text().strip()
                                stats[title] = value

                        await database.edit_player(
                            pid, 
                            name, 
                            position, 
                            team, 
                            number,
                        )
                    except Exception as e:
                        logging.error(e)
                return {
                    "status": response.status,
                    "player": {
                        "name": name,
                        "position": position,
                        "team": team,
                        "number": number,
                        "age": age,
                        "height": height,
                        "yc": stats.get("Yellow cards", "0"),
                        "rc": stats.get("Red cards", "0"),
                        "fouls": stats.get("Fouls", "0"),
                        "shots": stats.get("Shots", "0"),
                        "goals": stats.get("Goals", "0"),
                        "passes": stats.get("Passes", "0"),
                        "tackles": stats.get("Tackles", "0"),
                    },
                }
    raise HTTPException(404, "player not found")
