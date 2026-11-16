from sqlmodel import SQLModel, Field

class Deck(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str = ""
class DeckUpdate(SQLModel):
    name: str | None = None
    description: str | None = None

class Card(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    deck_id: int = Field(foreign_key="deck.id")
    front: str
    back: str