from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from project_paths import OUTPUT_DIR

from .routes import router


app = FastAPI(title="xhs_nail_agent API", version="0.1.0")
app.include_router(router)
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/", include_in_schema=False)
def web_index():
    return FileResponse(WEB_DIR / "index.html")


app.mount("/web", StaticFiles(directory=str(WEB_DIR)), name="web")
app.mount("/static/output", StaticFiles(directory=str(OUTPUT_DIR)), name="static-output")
