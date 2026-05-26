import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from api.routes.text_to_sign import text_router
from api.routes.Speech_to_text import speech_router

app = FastAPI(
    title="Text To Sign API",
    description="API for converting Arabic text/speech to sign language outputs.",
    version="1.0.0"
)

API_KEY = os.getenv("API_KEY")


@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    path = request.url.path

    # Public routes - no API key needed
    public_paths = [
        "/",
        "/docs",
        "/openapi.json",
        "/redoc",
    ]

    # Allow docs, static files, and root without API key
    if (
        path in public_paths
        or path.startswith("/static")
    ):
        return await call_next(request)

    # Protect all other routes
    client_api_key = request.headers.get("x-api-key")

    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Server API_KEY is not configured"
        )

    if client_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

    return await call_next(request)


@app.get("/")
def root():
    return {
        "message": "Text To Sign API is running",
        "docs": "/docs"
    }


app.include_router(text_router)
app.include_router(speech_router)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)
