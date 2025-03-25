from doctest import master

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.models import User
from database.utils import get_users, add_user_to_group

router = Router()

@router.message(Command("start"), StateFilter(None))
async def start(message: Message, state: FSMContext):
    await state.clear()
    msg_text = message.text

    referral = msg_text.split("/start")[1].strip()

    if referral != "":
        await add_user_to_group(str(message.from_user.id), referral)
        await message.answer(f"You have been added to group!")
    else:
        await message.answer(f"Hello!")