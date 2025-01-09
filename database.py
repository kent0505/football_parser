import aiosqlite

database: str = "sqlite.db"

async def create_tables():
    async with aiosqlite.connect(database) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            pid INTEGER NOT NULL,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            team TEXT NOT NULL,
            number INTEGER NOT NULL
        )
        """)
        await db.commit()

async def get_player(pid: int):
    async with aiosqlite.connect(database) as db:
        cursor = await db.execute("SELECT * FROM players WHERE pid = ?", (pid,))
        return await cursor.fetchone()
    
async def get_players():
    async with aiosqlite.connect(database) as db:
        cursor = await db.execute("SELECT * FROM players")
        return await cursor.fetchall()

async def add_player(
    pid: int, 
    name: str, 
    position: str,
    team: str,
    number: int,
):
    async with aiosqlite.connect(database) as db:
        cursor = await db.execute("SELECT * FROM players WHERE pid = ?", (pid,))
        row = await cursor.fetchone()
        if row: return
        await db.execute(
            "INSERT INTO players (pid, name, position, team, number) VALUES (?, ?, ?, ?, ?)", 
            (pid, name, position, team, number),
        )
        await db.commit()

async def edit_player(
    pid: int,
    name: str, 
    position: str,
    team: str,
    number: int,
):
    async with aiosqlite.connect(database) as db:
        await db.execute(
            "UPDATE players SET name = ?, position = ?, team = ?, number = ? WHERE pid = ?", 
            (name, position, team, number, pid),
        )
        await db.commit()

async def delete_player(pid: int):
    async with aiosqlite.connect(database) as db:
        await db.execute("DELETE FROM players WHERE pid = ?", (pid,))
        await db.commit()

# async def get_user(id: int) -> Optional[Tuple[int, str, str]]:
#     async with aiosqlite.connect(database) as db:
#         cursor = await db.execute("SELECT * FROM users WHERE id = ?", (id,))
#         return await cursor.fetchone()
