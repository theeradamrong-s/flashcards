from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from auth import create_access_token, get_current_user, hash_password, verify_password
from database import get_session
from models import Token, User, UserCreate, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    username = user_data.username.strip().lower()
    existing = session.exec(select(User).where(User.username == username)).first()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")
    user = User(username=username, password_hash=hash_password(user_data.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(user_data: UserCreate, session: Session = Depends(get_session)):
    username = user_data.username.strip().lower()
    user = session.exec(select(User).where(User.username == username)).first()
    # Same message for "no such user" and "wrong password", so attackers can't
    # find out which usernames exist
    if user is None or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong username or password")
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)):
    return user
