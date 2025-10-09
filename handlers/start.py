from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.utils import add_user_to_group

router = Router()

guide = """
To use this bot, firstly you need drop here any meme you wanna save!

Then you can access to this meme with: @inlinusbot <keywords>

All meme are sorted to groups, to sort them, use
@inlinusbot p <keywords>

All sort groups:

g - GIF
v - Videos
s - Stickers
a - Audios
p - Photos

Also you can create groups, to share meme with your friends, 
and only to your friends.
"""


@router.message(Command("start"), StateFilter("*"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    msg_text = message.text

    referral = msg_text.split("/start")[1].strip()

    if referral != "":
        await add_user_to_group(str(message.from_user.id), referral)
        await message.answer(f"You have been added to group!")
    else:
        await message.answer(f"Hello! \n" + guide)
