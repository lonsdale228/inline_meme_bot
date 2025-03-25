from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from database.utils import add_meme, get_user_groups
from handlers.add_to_groups import AddToGroup, add_meme_to_group

router = Router()

# class NamePicture(StatesGroup):
#     choosing_sticker_key_words = State()
#
# class NameGif(StatesGroup):
#     choosing_gif_key_words = State()

class NameMeme(StatesGroup):
    naming_meme = State()

# @router.message(F.sticker, StateFilter(None))
# async def sticker_handler(message: Message, state: FSMContext):
#
#     sticker_id = message.sticker.file_id
#
#     await state.update_data(sticker_id=sticker_id)
#
#     await message.answer("Enter sticker name/keywords")
#
#     await state.set_state(NamePicture.choosing_sticker_key_words)
#
# @router.message(F.text, StateFilter(NamePicture.choosing_sticker_key_words))
# async def get_sticker_name(message: Message, state: FSMContext):
#
#     data = await state.get_data()
#     sticker_name = message.text.strip()
#
#     is_added = await add_meme(title=sticker_name, description="", mime_type="sticker", file_id=data['sticker_id'], is_private=False,
#                               user_id=str(message.from_user.id))
#     if is_added:
#         await message.answer("Added!")
#     else:
#         await message.answer("Already exists!")
#
#     await state.clear()
#
#
#
#
# @router.message(F.animation, StateFilter(None))
# async def gif_handler(message: Message, state: FSMContext):
#     gif_id = message.animation.file_id
#
#     await state.update_data(gif_id=gif_id)
#
#     await message.answer("Enter gif name/keywords")
#
#     await state.set_state(NameGif.choosing_gif_key_words)
#
#
# @router.message(F.text, StateFilter(NameGif.choosing_gif_key_words))
# async def get_gif_name(message: Message, state: FSMContext):
#
#     data = await state.get_data()
#     gif_name = message.text.strip()
#
#     meme_id = await add_meme(title=gif_name, description="", mime_type="gif", file_id=data['gif_id'], is_private=False,
#                               user_id=str(message.from_user.id))
#     if meme_id != -1:
#         await message.answer(f"Added! {meme_id}")
#         await add_meme_to_group(message, state, meme_id)
#     else:
#         await message.answer("Already exists!")
#
#     await state.set_state(AddToGroup.add_meme_to_group)

@router.message(F.photo, StateFilter(None))
@router.message(F.audio, StateFilter(None))
@router.message(F.video, StateFilter(None))
@router.message(F.sticker, StateFilter(None))
@router.message(F.animation, StateFilter(None))
async def meme_handler(message: Message, state: FSMContext):

    async def send_msg(mime_type):
        await state.update_data(mime_type=mime_type)
        await message.answer("Enter meme name/keywords for future searching!")
        await state.set_state(NameMeme.naming_meme)


    if message.sticker:
        await state.update_data(meme_file_id=message.sticker.file_id)
        await send_msg("sticker")
        return
    if message.photo:
        await state.update_data(meme_file_id=message.photo[0].file_id)
        await send_msg("photo")
        return
    elif message.video:
        await state.update_data(meme_file_id=message.video.file_id)
        await send_msg("video")
        return
    elif message.animation:
        await state.update_data(meme_file_id=message.animation.file_id)
        await send_msg("gif")
        return
    elif message.audio:
        await state.update_data(meme_file_id=message.audio.file_id)
        await send_msg("audio")
        return
    else:
        await message.answer("Wrong file type!")
        return

@router.message(
    F.text,
    StateFilter(NameMeme.naming_meme)
)
async def add_uni_meme(message: Message, state: FSMContext):
    meme_name = message.text.strip()
    data = await state.get_data()

    meme_id = await add_meme(title=meme_name, description="", mime_type=data["mime_type"], file_id=data['meme_file_id'],
                             is_private=True,
                             user_id=str(message.from_user.id))

    if meme_id != -1:
        await state.set_state(AddToGroup.add_meme_to_group)

        if len(await get_user_groups(str(message.from_user.id)))!=0:
            await add_meme_to_group(message=message, state=state, meme_id=meme_id)
            # await state.clear()
        else:
            await message.answer("Added!")
            await state.clear()
    else:
        await message.answer("Already exists!")
        await state.clear()

