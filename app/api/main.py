from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import checkpoints, chapters, export, inputs, memory, projects, prompts, structure
from app.config import get_settings
from app.database.session import init_database

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(projects.router)
app.include_router(inputs.router)
app.include_router(structure.router)
app.include_router(chapters.router)
app.include_router(checkpoints.router)
app.include_router(export.router)
app.include_router(memory.router)
app.include_router(prompts.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}
