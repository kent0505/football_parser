from fastapi                 import FastAPI
from contextlib              import asynccontextmanager

from utils                   import *
from database                import create_tables
from routers.fixtures        import router as fixtures_router

import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    await create_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

app.include_router(fixtures_router, tags=["Fixtures"])
