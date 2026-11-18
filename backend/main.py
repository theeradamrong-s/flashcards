from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
from models import Deck, Card, DeckUpdate, CardCreate, CardUpdate

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

@app.patch("/decks/{deck_id}")
def update_deck(deck_id: int, deck_data: DeckUpdate, session: Session = Depends(get_session)):
    deck = session.get(Deck, deck_id)
    if deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    changes = deck_data.model_dump(exclude_unset=True)
    deck.sqlmodel_update(changes)                      
    session.add(deck)
    session.commit()
    session.refresh(deck)
    return deck

@app.delete("/decks/{deck_id}")
def delete_deck(deck_id: int, session: Session = Depends(get_session)):
    deck = session.get(Deck, deck_id)
    if deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    cards = session.exec(select(Card).where(Card.deck_id == deck_id)).all()
    for card in cards:
        session.delete(card)
    session.delete(deck)
    session.commit()
    return {"ok": True}

@app.post("/decks/{deck_id}/cards")
def create_card(deck_id: int, card_data: CardCreate, session: Session = Depends(get_session)):
    deck = session.get(Deck, deck_id)              
    if deck is None:                                 
        raise HTTPException(status_code=404, detail="Deck not found")
    card = Card(deck_id=deck_id, front=card_data.front, back=card_data.back)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card

@app.get("/decks/{deck_id}/cards")
def list_cards(deck_id: int, session: Session = Depends(get_session)):
    deck = session.get(Deck, deck_id)
    if deck is None:
        raise HTTPException(404, "Deck not found")
    cards = session.exec(select(Card).where(Card.deck_id == deck_id)).all()
    return cards

@app.patch("/cards/{card_id}")
def update_card(card_id: int, card_data: CardUpdate, session: Session = Depends(get_session)):
    card = session.get(Card, card_id)
    if card is None: 
        raise HTTPException(404, "Card not found")
    changes = card_data.model_dump(exclude_unset=True)
    card.sqlmodel_update(changes)                      
    session.add(card)
    session.commit()
    session.refresh(card)
    return card
    
@app.delete("/cards/{card_id}")
def delete_card(card_id: int, session: Session = Depends(get_session)):
    card = session.get(Card, card_id)
    if card is None:
        raise HTTPException(404, "Card not found")
    session.delete(card)
    session.commit()
    return {"ok": True}