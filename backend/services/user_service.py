"""
User service for database operations.
"""

from sqlalchemy.orm import Session
from models import User
from auth import hash_password, verify_password


def create_user(db: Session, username: str, email: str, password: str) -> User:
    """
    Create a new user with safely hashed password.
    """

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise ValueError("Email already registered")

    # Hash password safely
    hashed_password = hash_password(password)

    db_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        auth_provider="local"
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_google_id(db: Session, google_id: str) -> User | None:
    return db.query(User).filter(User.google_id == google_id).first()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Authenticate user safely.
    """

    user = get_user_by_email(db, email)

    if not user:
        return None

    if not user.password_hash:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def create_or_get_google_user(
    db: Session,
    google_id: str,
    email: str,
    username: str
) -> User:
    """
    Create or get Google authenticated user.
    """

    user = get_user_by_google_id(db, google_id)
    if user:
        return user

    # If email already exists, link Google account
    user = get_user_by_email(db, email)
    if user:
        user.google_id = google_id
        user.auth_provider = "google"
        db.commit()
        db.refresh(user)
        return user

    # Create new user
    db_user = User(
        username=username or email.split("@")[0],
        email=email,
        google_id=google_id,
        password_hash="",  # No password for Google users
        auth_provider="google"
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user