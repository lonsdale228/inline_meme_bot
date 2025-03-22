from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.sticker)
async def sticker_handler(message: Message):

    sticker_id = message.sticker.file_id
    await message.answer(sticker_id)


    # aud_id = message.audio.file_id
    # aud_name = message.caption
    # if aud_name == "":
    #     await message.answer("Name can`t be empty")
    #     return
    # is_added = await add_meme(title=aud_name, description="", mime_type="audio", file_id=aud_id, is_private=False, user_id=str(message.from_user.id))
    # if is_added:
    #     await message.answer("Added!")
    # else:
    #     await message.answer("Already exists!")
