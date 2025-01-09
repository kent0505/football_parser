from fastapi                 import FastAPI
from contextlib              import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from utils                   import *
from database                import create_tables
from routers.fixtures        import router as fixtures_router
from routers.players         import router as players_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

app.add_middleware(
    middleware_class  = CORSMiddleware,
    allow_credentials = True,
    allow_origins     = ["*"],
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

app.include_router(fixtures_router, tags=["Fixtures"])
app.include_router(players_router,  tags=["Players"])
