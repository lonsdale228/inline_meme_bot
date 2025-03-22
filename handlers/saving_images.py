from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from database.utils import add_meme

router = Router()

class NamePicture(StatesGroup):
    choosing_sticker_key_words = State()

class NameGif(StatesGroup):
    choosing_gif_key_words = State()

@router.message(F.sticker, StateFilter(None))
async def sticker_handler(message: Message, state: FSMContext):

    sticker_id = message.sticker.file_id

    await state.update_data(sticker_id=sticker_id)

    await message.answer("Enter sticker name/keywords")

    await state.set_state(NamePicture.choosing_sticker_key_words)

@router.message(F.text, StateFilter(NamePicture.choosing_sticker_key_words))
async def get_sticker_name(message: Message, state: FSMContext):

    data = await state.get_data()
    sticker_name = message.text.strip()

    is_added = await add_meme(title=sticker_name, description="", mime_type="sticker", file_id=data['sticker_id'], is_private=False,
                              user_id=str(message.from_user.id))
    if is_added:
        await message.answer("Added!")
    else:
        await message.answer("Already exists!")

    await state.clear()




@router.message(F.animation, StateFilter(None))
async def gif_handler(message: Message, state: FSMContext):
    gif_id = message.animation.file_id

    await state.update_data(gif_id=gif_id)

    await message.answer("Enter gif name/keywords")

    await state.set_state(NameGif.choosing_gif_key_words)


@router.message(F.text, StateFilter(NameGif.choosing_gif_key_words))
async def get_gif_name(message: Message, state: FSMContext):

    data = await state.get_data()
    gif_name = message.text.strip()

    is_added = await add_meme(title=gif_name, description="", mime_type="gif", file_id=data['gif_id'], is_private=False,
                              user_id=str(message.from_user.id))
    if is_added:
        await message.answer("Added!")
    else:
        await message.answer("Already exists!")

    await state.clear()
