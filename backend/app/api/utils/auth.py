from datetime import datetime

from fastapi import Depends, Cookie, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.services.session import SessionService
from app.services.users import UserService
from db.session import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


