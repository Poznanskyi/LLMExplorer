from typing import Type

from libgravatar import Gravatar
from slugify import slugify
from sqlalchemy.orm import Session

from api.database.models import User
from api.schemas import UserModel, UserUpdate


async def get_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session):
    try:
        g = Gravatar(body.email)
    except Exception as e:
        print(e)
    new_user = User(**body.dict())
    new_user.slug = slugify(body.username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def get_users(db: Session):
    return  db.query(User).all()


async def get_user_by_id(user_id: int, db: Session):
    return db.query(User).filter_by(id=user_id).first()


async def update(user_id: int, body: UserUpdate, db: Session):
    user = await get_user_by_id(user_id, db)
    if user:
        for field, value in body.dict().items():
            setattr(user, field, value)
        db.commit()
    return user


async def update_token(user: User, token: str | None, db: Session):
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> Type[User] | None:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user

async def invalidate_refresh_token(user, db: Session):
    """
    Invalidate the refresh token for the given user.
    """
    user.refresh_token = None  # Set the refresh_token to None or just delete it
    db.commit()
    return True

async def get_user_by_token(token: str, db: Session):
    return db.query(User).filter(User.refresh_token == token).first()