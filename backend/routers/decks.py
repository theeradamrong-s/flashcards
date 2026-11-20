from datetime import date

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, func, select

from auth import get_current_user
from database import get_session
from deps import get_owned_deck
from models import Card, Deck, DeckCreate, DeckPublic, DeckSummary, DeckUpdate, User

router = APIRouter(prefix="/decks", tags=["decks"])


@router.post("", response_model=DeckPublic, status_code=status.HTTP_201_CREATED)
def create_deck(
    deck_data: DeckCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    deck = Deck(name=deck_data.name, description=deck_data.description, user_id=user.id)
    session.add(deck)
    session.commit()
    session.refresh(deck)
    return deck


@router.get("", response_model=list[DeckSummary])
def list_decks(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    decks = session.exec(select(Deck).where(Deck.user_id == user.id).order_by(Deck.id)).all()
    today = date.today()
    summaries = []
    for deck in decks:
        card_count = session.exec(
            select(func.count()).select_from(Card).where(Card.deck_id == deck.id)
        ).one()
        due_count = session.exec(
            select(func.count()).select_from(Card)
            .where(Card.deck_id == deck.id, Card.due_date <= today)
        ).one()
        summaries.append(DeckSummary(
            id=deck.id, name=deck.name, description=deck.description,
            card_count=card_count, due_count=due_count,
        ))
    return summaries


@router.get("/{deck_id}", response_model=DeckPublic)
def read_deck(deck: Deck = Depends(get_owned_deck)):
    return deck


@router.patch("/{deck_id}", response_model=DeckPublic)
def update_deck(
    deck_data: DeckUpdate,
    deck: Deck = Depends(get_owned_deck),
    session: Session = Depends(get_session),
):
    changes = deck_data.model_dump(exclude_unset=True)
    deck.sqlmodel_update(changes)
    session.add(deck)
    session.commit()
    session.refresh(deck)
    return deck


@router.delete("/{deck_id}")
def delete_deck(
    deck: Deck = Depends(get_owned_deck),
    session: Session = Depends(get_session),
):
    # Delete the cards first so none are left pointing at a missing deck
    cards = session.exec(select(Card).where(Card.deck_id == deck.id)).all()
    for card in cards:
        session.delete(card)
    session.delete(deck)
    session.commit()
    return {"ok": True}
