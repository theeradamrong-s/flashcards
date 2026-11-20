from datetime import date

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

import sm2
from database import get_session
from deps import get_owned_card, get_owned_deck
from models import Card, Deck, ReviewRequest

router = APIRouter(tags=["study"])


@router.get("/decks/{deck_id}/due", response_model=list[Card])
def due_cards(
    deck: Deck = Depends(get_owned_deck),
    session: Session = Depends(get_session),
):
    """Cards in this deck that are due today or overdue, oldest first."""
    return session.exec(
        select(Card)
        .where(Card.deck_id == deck.id, Card.due_date <= date.today())
        .order_by(Card.due_date, Card.id)
    ).all()


@router.post("/cards/{card_id}/review", response_model=Card)
def review_card(
    review: ReviewRequest,
    card: Card = Depends(get_owned_card),
    session: Session = Depends(get_session),
):
    """Record how well the card was remembered and schedule its next review."""
    result = sm2.review(
        ease_factor=card.ease_factor,
        interval=card.interval,
        repetitions=card.repetitions,
        quality=review.quality,
        today=date.today(),
    )
    card.ease_factor = result.ease_factor
    card.interval = result.interval
    card.repetitions = result.repetitions
    card.due_date = result.due_date
    session.add(card)
    session.commit()
    session.refresh(card)
    return card
