from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from routes import auth, intern, mentor, hr

Base.metadata.create_all(bind=engine)

app = FastAPI(title="实习生成长导航")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router)
app.include_router(intern.router)
app.include_router(mentor.router)
app.include_router(hr.router)

# Serve frontend static files LAST (catch-all for /)
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
