# Flashcards

A full-stack flashcard web app for creating decks and studying cards with spaced repetition.

**Built with:** Vue 3, Vue Router, Pinia, FastAPI, SQLModel, SQLite, JWT, pytest

## Features
- Register and log in; each user only sees their own decks
- Create, edit and delete decks and cards
- Study mode: flip a card and rate it Again / Hard / Good / Easy
- Each card's next review date is scheduled with the SM-2 algorithm
- Deck list shows how many cards are due today

## Running locally

**Backend** (Python 3.12+):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

**Frontend** (Node 22+), in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and create an account.

**Tests:**

```bash
cd backend && source .venv/bin/activate && pytest
```

### Configuration

| Variable | Where | Default |
|---|---|---|
| `SECRET_KEY` | backend | a dev-only key. **Set a long random value in production.** |
| `DATABASE_URL` | backend | `sqlite:///flashcards.db` |
| `ALLOWED_ORIGINS` | backend | `http://localhost:5173` (comma-separated) |
| `VITE_API_URL` | frontend | `http://127.0.0.1:8001` |
