from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
from models import Deck, Card

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()   # run when start
    yield                  

app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"message": "Flashcards API is running"}

@app.post("/decks")
def create_deck(deck: Deck, session: Session = Depends(get_session)):
    session.add(deck)      
    session.commit()       
    session.refresh(deck)   
    return deck

@app.get("/decks")
def list_decks(session: Session = Depends(get_session)):
    decks = session.exec(select(Deck)).all()
    return decks

@app.get("/decks/{deck_id}")
def read_deck(deck_id: int, session: Session = Depends(get_session)):
    deck = session.get(Deck, deck_id)
    if (not deck):
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck