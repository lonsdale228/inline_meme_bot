from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.models import User
from database.utils import get_users

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    users: list[User] = await get_users()

    user_id = message.from_user.id

    for user in users:
        if user.user_id == str(user_id):
            await message.answer("You are logged in!")
            return
