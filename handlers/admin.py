from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("add_user"))
async def add_user_admin(message: Message): ...
