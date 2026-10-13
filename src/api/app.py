import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import auth, bookings, masters, services, slots

app = FastAPI(
    title="Sense Nail Studio API",
    description="REST API for Sense Nail Studio Telegram Mini App",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api
api_router = FastAPI()
app.include_router(services.router, prefix="/api")
app.include_router(masters.router, prefix="/api")
app.include_router(slots.router, prefix="/api")
app.include_router(bookings.router, prefix="/api")
app.include_router(auth.router, prefix="/api")


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to /app/."""
    return RedirectResponse(url="/app/")


# Serve frontend/dist as static files under /app
dist_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
)
if os.path.exists(dist_path):
    app.mount("/app", StaticFiles(directory=dist_path, html=True), name="frontend")
else:
    @app.get("/app", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/app/", response_class=HTMLResponse, include_in_schema=False)
    async def app_placeholder():
        return "<h3>Telegram Mini App is building... Please run 'npm run build' in frontend/.</h3>"
