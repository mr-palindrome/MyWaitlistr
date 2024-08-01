import random
import string
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from fastapi import HTTPException, status, Depends
import jwt

from src.config import settings
from .models import User, Token
from .schemas.user_schema import CeateUserSchema
from .utils.password import secure_pwd, verify_pwd, oauth2_scheme


def get_user_by_username(db: Session, username: str):
    """
    Get a user by username from the database.

    Args:
        db (Session): The database session.
        username (str): The username of the user.

    Returns:
        User: The user object.
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    """
    Get a user by email from the database.

    Args:
        db (Session): The database session.
        email (str): The email of the user.

    Returns:
        User: The user object.
    """
    return db.query(User).filter(User.email == email).first()


def verify_user(db: Session, email: str, password: str):
    """
    Verify the user by username and password.

    Args:
        db (Session): The database session.
        email (str): The email of the user.
        password (str): The password of the user.

    Returns:
        User: The user object.
    """
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_pwd(password, user.hashed_password):
        return False
    return user


def create_user(db: Session, user: CeateUserSchema):
    """
    Create a new user in the database.

    Args:
        db (Session): The database session.
        user (CeateUserSchema): The user data to be created.

    Returns:
        User: The newly created user object.
    """
    _user = User(username=user.username, email=user.email, full_name=user.full_name, img_url=user.img_url)
    hassed_password = secure_pwd(user.password)
    _user.hashed_password = hassed_password
    db.add(_user)
    db.commit()
    db.refresh(_user)
    return _user


def update_password(db: Session, user: User, new_password: str):
    """
    Update the password of the user.

    Args:
        db (Session): The database session.
        user (User): The user object.
        new_password (str): The new password.

    Returns:
        User: The updated user object.
    """
    hashed_password = secure_pwd(new_password)
    user.hashed_password = hashed_password
    db.commit()
    return user

def get_token(db: Session, token: str):
    """
    Get a token by token from the database.

    Args:
        db (Session): The database session.
        token (str): The token.

    Returns:
        Token: The token object.
    """
    return db.query(Token).filter(Token.token == token).firt()


def create_token(db: Session, token: str, user_id: int):
    """
    Create a new token in the database.

    Args:
        db (Session): The database session.
        token (str): The token.
        user_id (int): The user id.

    Returns:
        Token: The newly created token object.
    """
    _token = Token(token=token, user_id=user_id)
    db.add(_token)
    db.commit()
    db.refresh(_token)
    return _token


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError as exc:
        raise credentials_exception from exc
    user = get_user_by_username(db=db, username=username)
    if user is None:
        raise credentials_exception
    return user

def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits + "@$&#!-_"
    return "".join(random.choice(characters) for i in range(length))
