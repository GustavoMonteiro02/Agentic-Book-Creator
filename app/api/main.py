from fastapi import FastAPI

from app.api.routes import chapters, export, inputs, memory, projects, structure
from app.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.include_router(projects.router)
app.include_router(inputs.router)
app.include_router(structure.router)
app.include_router(chapters.router)
app.include_router(export.router)
app.include_router(memory.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}
