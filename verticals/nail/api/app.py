from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from project_paths import OUTPUT_DIR

from .routes import router


app = FastAPI(title="xhs_nail_agent API", version="0.1.0")
app.include_router(router)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static/output", StaticFiles(directory=str(OUTPUT_DIR)), name="static-output")
