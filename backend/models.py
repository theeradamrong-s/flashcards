from datetime import date

from sqlmodel import SQLModel, Field


# ---------- Users ----------

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str

class UserCreate(SQLModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6, max_length=128)

class UserPublic(SQLModel):
    id: int
    username: str

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Decks ----------

class Deck(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str = ""
    user_id: int = Field(foreign_key="user.id", index=True)

class DeckCreate(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)

class DeckUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)

class DeckPublic(SQLModel):
    id: int
    name: str
    description: str

class DeckSummary(DeckPublic):
    card_count: int
    due_count: int


# ---------- Cards ----------

class Card(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    deck_id: int = Field(foreign_key="deck.id", index=True)
    front: str
    back: str
    # SM-2 scheduling state
    ease_factor: float = 2.5
    interval: int = 0          # days until the next review
    repetitions: int = 0       # correct answers in a row
    due_date: date = Field(default_factory=date.today)

class CardCreate(SQLModel):
    front: str = Field(min_length=1, max_length=1000)
    back: str = Field(min_length=1, max_length=1000)

class CardUpdate(SQLModel):
    front: str | None = Field(default=None, min_length=1, max_length=1000)
    back: str | None = Field(default=None, min_length=1, max_length=1000)

class ReviewRequest(SQLModel):
    quality: int = Field(ge=0, le=5)   # 0 = total blackout, 5 = perfect recall
