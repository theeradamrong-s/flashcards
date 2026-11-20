import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_db_and_tables
from routers import cards, decks, study, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()   # run when the server starts
    yield

app = FastAPI(title="Flashcards API", lifespan=lifespan)

# Which frontends may call this API (comma-separated), default = the Vue dev server
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(decks.router)
app.include_router(cards.router)
app.include_router(study.router)


@app.get("/")
def home():
    return {"message": "Flashcards API is running"}
