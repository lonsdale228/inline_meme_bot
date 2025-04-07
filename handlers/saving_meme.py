from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from database.utils import add_meme, get_user_groups
from filters.chat_type import ChatTypeFilter
from handlers.add_to_groups import AddToGroup, add_meme_to_group

router = Router()
router.message.filter(ChatTypeFilter(chat_type=["sender", "private"]))

class NameMeme(StatesGroup):
    naming_meme = State()



@router.message(F.photo, StateFilter(None))
@router.message(F.audio, StateFilter(None))
@router.message(F.video, StateFilter(None))
@router.message(F.sticker, StateFilter(None))
@router.message(F.animation, StateFilter(None))
async def meme_handler(message: Message, state: FSMContext):
    await message.answer(str(message.chat.id))
    async def send_msg(mime_type):
        await state.update_data(mime_type=mime_type)
        await message.answer("Enter meme name/keywords for future searching!")
        await state.set_state(NameMeme.naming_meme)


    if message.sticker:
        await state.update_data(meme_file_id=message.sticker.file_id)
        await state.update_data(meme_unique_file_id=message.sticker.file_unique_id)
        await send_msg("sticker")
        return
    if message.photo:
        await state.update_data(meme_file_id=message.photo[0].file_id)
        await state.update_data(meme_unique_file_id=message.photo[0].file_unique_id)
        await send_msg("photo")
        return
    elif message.video:
        await state.update_data(meme_file_id=message.video.file_id)
        await state.update_data(meme_unique_file_id=message.video.file_unique_id)
        await send_msg("video")
        return
    elif message.animation:
        await state.update_data(meme_file_id=message.animation.file_id)
        await state.update_data(meme_unique_file_id=message.animation.file_unique_id)
        await send_msg("gif")
        return
    elif message.audio:
        await state.update_data(meme_file_id=message.audio.file_id)
        await state.update_data(meme_unique_file_id=message.audio.file_unique_id)
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
                             user_id=str(message.from_user.id), file_unique_id=data['meme_unique_file_id'])

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

