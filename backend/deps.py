"""Shared lookups that also check the logged-in user owns the deck or card.

Someone else's deck gets the same 404 as a missing one, so users can't
discover which deck ids exist.
"""

from fastapi import Depends, HTTPException
from sqlmodel import Session

from auth import get_current_user
from database import get_session
from models import Card, Deck, User


def get_owned_deck(
    deck_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Deck:
    deck = session.get(Deck, deck_id)
    if deck is None or deck.user_id != user.id:
        raise HTTPException(404, "Deck not found")
    return deck


def get_owned_card(
    card_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Card:
    card = session.get(Card, card_id)
    if card is None:
        raise HTTPException(404, "Card not found")
    deck = session.get(Deck, card.deck_id)
    if deck is None or deck.user_id != user.id:
        raise HTTPException(404, "Card not found")
    return card
