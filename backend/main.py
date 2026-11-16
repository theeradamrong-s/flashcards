from contextlib import asynccontextmanager
from fastapi import FastAPI

from database import create_db_and_tables
import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()   # run when start
    yield                  

app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"message": "Flashcards API is running"}