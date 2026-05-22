from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import worksheet
from config import APP_NAME, VERSION

app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    description="AI powered worksheet generator for college students"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(worksheet.router, prefix="/api/worksheet", tags=["worksheet"])

@app.get("/")
def home():
    return {
        "app": APP_NAME,
        "version": VERSION,
        "status": "running"
    }