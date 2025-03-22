import sqlalchemy
from sqlalchemy import select, Boolean, bindparam
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import sessionmanager, get_session
from database.models import Meme, User
from loader import logger


async def add_meme(title: str, description: str, file_id: str, mime_type: str, user_id: str, is_private: bool = False) -> bool:
    try:
        async with sessionmanager.session() as session:
            session.add(Meme(title=title, description=description, file_id=file_id, mime_type=mime_type, user_id=user_id, is_private=is_private))
            await session.commit()
            return True
    except sqlalchemy.exc.IntegrityError:
        logger.info("Value already exists!")
        return False


async def get_memes(search_text: str, media_type: str):
    async for session in get_session():
        result = await session.execute(select(Meme).where(Meme.title.ilike(f"%{search_text}%")).where(Meme.mime_type==media_type))
        return result.scalars().all()


async def add_user(user_id, is_admin: bool):
    try:
        async for session in get_session():
            session.add(User(user_id=user_id, is_admin=is_admin))
            await session.commit()
            return True
    except sqlalchemy.exc.IntegrityError:
        logger.info("User already exists!")
        return False


async def get_users():
    async for session in get_session():
        result = await session.execute(select(User))
        return result.scalars().all()