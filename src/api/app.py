import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from src.api.routes import auth, bookings, masters, services, slots
from src.config import settings
from src.database.session import async_session_maker

app = FastAPI(
    title="Sense Nail Studio API",
    description="REST API for Sense Nail Studio Telegram Mini App",
    version=settings.APP_VERSION,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Enforce standard security HTTP headers."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Telegram Mini Apps run inside iframes on Telegram Web and WebView.
    # X-Frame-Options: SAMEORIGIN blocks Telegram from rendering the Mini App.
    if request.url.path.startswith("/app"):
        response.headers["Content-Security-Policy"] = (
            "frame-ancestors 'self' https://web.telegram.org https://*.telegram.org telegram:;"
        )
    else:
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response


# Include API Routers under /api
api_router = FastAPI()
app.include_router(services.router, prefix="/api")
app.include_router(masters.router, prefix="/api")
app.include_router(slots.router, prefix="/api")
app.include_router(bookings.router, prefix="/api")
app.include_router(auth.router, prefix="/api")


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
async def healthcheck():
    """Health check endpoint verifying database connectivity and service health."""
    db_status = "connected"
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": db_status,
                "version": settings.APP_VERSION,
            },
        )
    return {
        "status": "healthy",
        "database": db_status,
        "salon": settings.SALON_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to /app/."""
    return RedirectResponse(url="/app/")


INDEX_CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
}

IMMUTABLE_CACHE_HEADERS = {
    "Cache-Control": "public, max-age=31536000, immutable",
}

dist_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
)
assets_path = os.path.join(dist_path, "assets")


class ImmutableStaticFiles(StaticFiles):
    def file_response(self, full_path, stat_result, scope, status_code: int = 200):
        response = super().file_response(full_path, stat_result, scope, status_code)
        response.headers.update(IMMUTABLE_CACHE_HEADERS)
        return response


# Mount hashed assets under /app/assets with immutable long-term caching
if os.path.exists(assets_path):
    app.mount("/app/assets", ImmutableStaticFiles(directory=assets_path), name="assets")


# Explicit endpoints for index.html with strict anti-cache headers
@app.api_route("/app", methods=["GET", "HEAD"], include_in_schema=False)
@app.api_route("/app/", methods=["GET", "HEAD"], include_in_schema=False)
async def serve_app_index():
    index_file = os.path.join(dist_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file, media_type="text/html", headers=INDEX_CACHE_HEADERS)
    return HTMLResponse(
        "<h3>Telegram Mini App is building... Please run 'npm run build' in frontend/.</h3>"
    )


# Fallback handler for any other static files or client-side SPA routes under /app
@app.api_route("/app/{full_path:path}", methods=["GET", "HEAD"], include_in_schema=False)
async def serve_app_spa_fallback(full_path: str):
    file_path = os.path.join(dist_path, full_path)
    if os.path.isfile(file_path):
        if full_path.endswith(".html"):
            return FileResponse(file_path, media_type="text/html", headers=INDEX_CACHE_HEADERS)
        elif full_path.startswith("assets/"):
            return FileResponse(file_path, headers=IMMUTABLE_CACHE_HEADERS)
        return FileResponse(file_path)

    # SPA fallback to index.html
    index_file = os.path.join(dist_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file, media_type="text/html", headers=INDEX_CACHE_HEADERS)
    return HTMLResponse("<h3>File not found</h3>", status_code=404)
