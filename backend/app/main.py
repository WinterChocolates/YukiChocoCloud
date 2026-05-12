from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers import auth, files, share, upload

app = FastAPI()

app.include_router(auth.router)
app.include_router(files.router)
app.include_router(upload.router)
app.include_router(share.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


STATIC_DIR = Path(__file__).resolve().parent / "static"

if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file = STATIC_DIR / full_path
        if file.is_file():
            return FileResponse(file)
        return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
