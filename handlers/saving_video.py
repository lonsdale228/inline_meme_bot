from aiogram import F, Router

from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultVideo, Message

from database.utils import add_meme
# router = Router()


# @router.message(F.video)
# async def video_handler(message: Message):
#     vid_id = message.video.file_id
#     vid_name = message.caption
#     if vid_name == "":
#         await message.answer("Name can`t be empty")
#         return
#     is_added = await add_meme(title=vid_name, description="", mime_type="video", file_id=vid_id, is_private=False, user_id=str(message.from_user.id))
#     if is_added:
#         await message.answer("Added!")
#     else:
#         await message.answer("Already exists!")
#
#
#
# @router.message(F.audio)
# async def audio_handler(message: Message):
#     aud_id = message.audio.file_id
#     aud_name = message.caption
#     if aud_name == "":
#         await message.answer("Name can`t be empty")
#         return
#     is_added = await add_meme(title=aud_name, description="", mime_type="audio", file_id=aud_id, is_private=False, user_id=str(message.from_user.id))
#     if is_added:
#         await message.answer("Added!")
#     else:
#         await message.answer("Already exists!")
