from fastapi          import FastAPI
from contextlib       import asynccontextmanager

from utils            import *
from database         import create_tables
from routers.fixtures import router as fixtures_router
from routers.players  import router as players_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

app.include_router(fixtures_router, tags=["Fixtures"])
app.include_router(players_router,  tags=["Players"])
