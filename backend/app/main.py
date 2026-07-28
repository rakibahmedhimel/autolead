import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app import models
from backend.app.config import FRONTEND_URL
from backend.app.routers.auth import router as auth_router
from backend.app.routers.dashboard import router as dashboard_router
from backend.app.routers.jobs import router as job_router
from backend.app.routers.projects import router as projects_router
from backend.app.routers.settings import router as settings_router
from backend.app.routers.spreadsheets import router as spreadsheets_router
from backend.app.routers.submissions import router as submissions_router

app = FastAPI()

frontend_url = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173",
)

allowed_origins = [
    "http://localhost:5173",
    frontend_url,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(job_router)
app.include_router(projects_router)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(settings_router)
app.include_router(submissions_router)
app.include_router(spreadsheets_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
