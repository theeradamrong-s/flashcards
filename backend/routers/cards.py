from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from database import get_session
from deps import get_owned_card, get_owned_deck
from models import Card, CardCreate, CardUpdate, Deck

router = APIRouter(tags=["cards"])


@router.post("/decks/{deck_id}/cards", response_model=Card, status_code=status.HTTP_201_CREATED)
def create_card(
    card_data: CardCreate,
    deck: Deck = Depends(get_owned_deck),
    session: Session = Depends(get_session),
):
    card = Card(deck_id=deck.id, front=card_data.front, back=card_data.back)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


@router.get("/decks/{deck_id}/cards", response_model=list[Card])
def list_cards(
    deck: Deck = Depends(get_owned_deck),
    session: Session = Depends(get_session),
):
    return session.exec(select(Card).where(Card.deck_id == deck.id).order_by(Card.id)).all()


@router.patch("/cards/{card_id}", response_model=Card)
def update_card(
    card_data: CardUpdate,
    card: Card = Depends(get_owned_card),
    session: Session = Depends(get_session),
):
    changes = card_data.model_dump(exclude_unset=True)
    card.sqlmodel_update(changes)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


@router.delete("/cards/{card_id}")
def delete_card(
    card: Card = Depends(get_owned_card),
    session: Session = Depends(get_session),
):
    session.delete(card)
    session.commit()
    return {"ok": True}
