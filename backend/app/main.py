from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers.projects import router as projects_router
from backend.app.routers.jobs import router as job_router
from backend.app.routers.auth import router as auth_router
from backend.app.routers.dashboard import router as dashboard_router
from backend.app.routers.settings import router as settings_router
from backend.app.routers.submissions import router as submissions_router
from backend.app.routers.spreadsheets import router as spreadsheets_router
from backend.app import models

app = FastAPI()

origins = [

    "http://localhost:3000",

    "http://localhost:5173",

    "https://autolead-pearl.vercel.app"

]


app.add_middleware(

    CORSMiddleware,

    allow_origins=origins,

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
