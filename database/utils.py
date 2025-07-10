import secrets

import sqlalchemy
from sqlalchemy import select, Boolean, bindparam, delete, distinct, text, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import sessionmanager, get_session
from database.models import Meme, User, Group, UserGroup, GroupMeme
from loader import logger


async def add_meme(
    title: str,
    description: str,
    file_id: str,
    file_unique_id: str,
    mime_type: str,
    user_id: str,
    is_private: bool = False,
) -> int:
    try:
        session: AsyncSession
        async for session in get_session():
            try:
                await add_user(user_id, False)
            except Exception as e:
                ...

            meme = Meme(
                name=title,
                file_id=file_id,
                file_unique_id=file_unique_id,
                mime_type=mime_type,
                user_tg_id=user_id,
                is_public=(not is_private),
            )
            session.add(meme)
            await session.flush()
            meme_id: int = meme.id
            await session.commit()
            return meme_id
    except sqlalchemy.exc.IntegrityError:
        logger.info("Value already exists!")
        return -1


# group = Group(name=group_name, admin_id=user_id, invite_link_id=secrets.token_hex(16))
# session.add(group)
# await session.flush()
#
# user_group = UserGroup(user_id=user_id, group_id=group.id)
# session.add(user_group)
# await session.commit()
# return True
# async def get_all_user_memes(user_id: str):
#     async for session in get_session():
#         query = (
#             select(Meme)
#             .distinct(Meme.id)
#             .join(GroupMeme, GroupMeme.meme_id == Meme.id)
#             .join(Group, Group.id == GroupMeme.group_id)
#             .join(UserGroup, UserGroup.group_id == Group.id)
#             .where(UserGroup.user_id == user_id)
#             .where(Meme.user_tg_id == user_id)
#         )
#         result = await session.execute(query)
#         return result.scalars().all()


async def get_memes(search_text: str, media_type: str, user_id: str):
    words = [word.strip() for word in search_text.split() if word.strip()]

    async for session in get_session():
        query = (
            select(Meme)
            .distinct(Meme.id)
            .join(GroupMeme, GroupMeme.meme_id == Meme.id, isouter=True)
            .join(Group, Group.id == GroupMeme.group_id, isouter=True)
            .join(UserGroup, UserGroup.group_id == Group.id, isouter=True)
            .where(
                or_(
                    (
                        (UserGroup.user_id == user_id)
                        & (
                            (Meme.mime_type == media_type)
                            if media_type != "*"
                            else True
                        )
                        & and_(*[Meme.name.ilike(f"%{word}%") for word in words])
                        if search_text != "*"
                        else True
                    ),
                    (
                        (Meme.user_tg_id == user_id)
                        & (
                            (Meme.mime_type == media_type)
                            if media_type != "*"
                            else True
                        )
                        & and_(*[Meme.name.ilike(f"%{word}%") for word in words])
                        if search_text != "*"
                        else True
                    ),
                )
            )
        )

        result = await session.execute(query)
        return result.scalars().all()


async def add_user(user_id, is_admin: bool):
    try:
        async for session in get_session():
            session.add(User(tg_id=user_id))
            await session.commit()
            return True
    except sqlalchemy.exc.IntegrityError:
        logger.info("User already exists!")
        return False


async def get_users():
    async for session in get_session():
        result = await session.execute(select(User))
        return result.scalars().all()


async def create_group(user_id: str, group_name: str, token: str) -> bool:
    try:
        async for session in get_session():
            group = Group(name=group_name, admin_id=user_id, invite_link_id=token)
            session.add(group)
            await session.flush()

            user_group = UserGroup(user_id=user_id, group_id=group.id)
            session.add(user_group)
            await session.commit()
            return True
    except sqlalchemy.exc.IntegrityError:
        logger.info("Value already exists!")
        return False


async def add_user_to_group(user_id: str, invite_link_id: str):
    async for session in get_session():
        result = await session.execute(
            select(Group).where(Group.invite_link_id == invite_link_id)
        )
        group: Group = result.scalars().first()

        session.add(UserGroup(user_id=user_id, group_id=group.id))
        await session.commit()


async def add_meme_to_all_user_groups(user_id: str, meme_id: int):
    async for session in get_session():
        result = await get_user_groups(user_id)

        for group in result:
            session.add(GroupMeme(meme_id=meme_id, group_id=group.id))

        await session.commit()


async def get_user_groups(user_id: str) -> list[Group]:
    async for session in get_session():
        result = await session.execute(
            select(Group)
            .join(UserGroup, Group.id == UserGroup.group_id)
            .where(UserGroup.user_id == user_id)
        )
        return result.scalars().all()


async def send_meme_to_selected_group(groups_id: list[int], meme_id: int):
    async for session in get_session():
        for group_id in groups_id:
            session.add(GroupMeme(group_id=group_id, meme_id=meme_id))

        await session.commit()


async def send_meme_to_all(user_id: str, meme_id: int):
    async for session in get_session():
        user_groups = await get_user_groups(user_id)
        for group in user_groups:
            session.add(GroupMeme(group_id=group.id, meme_id=meme_id))

        await session.commit()


async def delete_group(group_id: int, user_id: str) -> bool:
    admin_groups = await get_group_admin(group_id, user_id)
    if admin_groups:
        async for session in get_session():
            res = await session.execute(
                select(Meme)
                .join(GroupMeme, Meme.id == GroupMeme.meme_id)
                .where(GroupMeme.group_id == group_id)
            )

            memes: tuple[Meme] = res.scalars().all()

            await session.execute(
                delete(GroupMeme).where(GroupMeme.group_id == group_id)
            )
            await session.execute(
                delete(UserGroup).where(UserGroup.group_id == group_id)
            )
            await session.execute(delete(Group).where(Group.id == group_id))

            for memasik in memes:
                await session.execute(delete(Meme).where(Meme.id == memasik.id))
            await session.commit()
        return True
    else:
        return False


async def delete_meme(meme_unique_file_id: str, user_id: str) -> bool:
    async for session in get_session():
        result = await session.execute(
            select(Meme).where(Meme.file_unique_id == meme_unique_file_id)
        )

        meme: Meme = result.scalars().first()

        if meme.user_tg_id == user_id:
            await session.delete(meme)
            await session.commit()
            return True
        else:
            return False


async def get_group_admin(group_id: int, user_id: str):
    async for session in get_session():
        result = await session.execute(select(Group).where(Group.admin_id == user_id).where(Group.id == group_id))
        return result.scalars().all()