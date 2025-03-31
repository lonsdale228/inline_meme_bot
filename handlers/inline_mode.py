import random
from datetime import datetime

from aiogram import F, Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultVideo, \
    InlineQueryResultCachedVideo, InlineQueryResultCachedAudio, InlineQueryResultCachedDocument, InlineQueryResultCachedSticker, InlineQueryResultCachedGif,InlineQueryResultCachedPhoto

from database.connection import get_session
from database.models import Meme
from database.utils import get_memes
from loader import logger, bot

router = Router()



# @router.inline_query(F.query=="")
# async def show_possible_commands(inline_query: InlineQuery):
#     results = []
#
#     available_commands = {
#         "meme": "Show video meme",
#         "ameme": "Show audio meme",
#         "gif": "Show gif",
#         "st": "Show stickers",
#     }
#
#
#     for i, (command, desc) in enumerate(available_commands.items()):
#         results.append(
#             InlineQueryResultArticle(
#                 id = str(i),
#                 title = command,
#                 description = desc,
#                 input_message_content = InputTextMessageContent(
#                     message_text="it just a hint, dont click on it",
#                 ),
#             )
#         )
#     await inline_query.answer(results, cache_time=0, is_personal=True)

@router.inline_query(F.query=="a")
@router.inline_query(F.query=="v")
@router.inline_query(F.query=="p")
@router.inline_query(F.query=="s")
@router.inline_query(F.query=="g")
async def show_sorted_memes(inline_query: InlineQuery):
    results = []

    query = inline_query.query.strip()
    user_id = str(inline_query.from_user.id)
    try:
        search_text = query.split(" ", 1)[1]
    except IndexError:
        search_text = ""

    match query:
        case "s":
            meme_list = await get_memes(search_text, "sticker", user_id)
            for meme in meme_list:
                results.append(InlineQueryResultCachedSticker(
                    sticker_file_id=meme.file_id,
                    title=meme.name,
                    id=str(meme.id)
                ))
        case "v":
            meme_list = await get_memes(search_text, "video", user_id)
            meme: Meme
            for meme in meme_list:
                results.append(InlineQueryResultCachedVideo(
                    title=meme.name,
                    video_file_id=meme.file_id,
                    id=str(meme.id)
                ))
        case "a":
            meme_list = await get_memes(search_text, "audio", user_id)
            for meme in meme_list:
                results.append(InlineQueryResultCachedDocument(
                    caption=meme.name,
                    title=meme.name,
                    document_file_id=meme.file_id,
                    description=meme.name,
                    id=str(meme.id)
                ))
        case "p":
            meme_list = await get_memes(search_text, "photo", user_id)
            for meme in meme_list:
                results.append(InlineQueryResultCachedPhoto(
                    title=meme.name,
                    photo_file_id=meme.file_id,
                    id=str(meme.id)
                ))
        case "g":
            meme_list = await get_memes(search_text, "gif", user_id)
            for meme in meme_list:
                results.append(InlineQueryResultCachedGif(
                    title=meme.name,
                    gif_file_id=meme.file_id,
                    id=str(meme.id)
                ))

    await inline_query.answer(results, cache_time=0, is_personal=True)

# @router.inline_query(F.query.startswith("meme"))
# async def show_user_videos(inline_query: InlineQuery):
#     results = []
#
#     search_text = inline_query.query.replace("meme", "").strip()
#
#     meme_list = await get_memes(search_text, "video", str(inline_query.from_user.id))
#     logger.info(meme_list)
#
#     meme: Meme
#     for meme in meme_list:
#         results.append(InlineQueryResultCachedVideo(
#             title=meme.name,
#             video_file_id=meme.file_id,
#             id=str(meme.id)
#        ))
#     await inline_query.answer(results, cache_time=0, is_personal=True)
#
#
#
# @router.inline_query(F.query.startswith("ameme"))
# async def show_user_audios(inline_query: InlineQuery):
#     results = []
#
#     search_text = inline_query.query.replace("ameme", "").strip()
#
#     meme_list = await get_memes(search_text, "audio", str(inline_query.from_user.id))
#     logger.info(meme_list)
#     for meme in meme_list:
#         results.append(InlineQueryResultCachedDocument(
#             caption=meme.name,
#             title=meme.name,
#             document_file_id=meme.file_id,
#             description=meme.name,
#             id=str(meme.id)
#        ))
#     await inline_query.answer(results, cache_time=0, is_personal=True)
#
#
#
# @router.inline_query(F.query.startswith("st"))
# async def show_user_stickers(inline_query: InlineQuery):
#     results = []
#
#     search_text = inline_query.query.replace("st", "").strip()
#
#     meme_list = await get_memes(search_text, "sticker", str(inline_query.from_user.id))
#     logger.info(meme_list)
#     for meme in meme_list:
#         results.append(InlineQueryResultCachedSticker(
#             sticker_file_id=meme.file_id,
#             title=meme.name,
#             id=str(meme.id)
#        ))
#     await inline_query.answer(results, cache_time=0, is_personal=True)
#
#
# @router.inline_query(F.query.startswith("gif"))
# async def show_user_gifs(inline_query: InlineQuery):
#     results = []
#
#     search_text = inline_query.query.replace("gif", "").strip()
#
#     meme_list = await get_memes(search_text, "gif", str(inline_query.from_user.id))
#     logger.info(meme_list)
#     for meme in meme_list:
#         results.append(InlineQueryResultCachedGif(
#             title=meme.name,
#             gif_file_id=meme.file_id,
#             id=str(meme.id)
#        ))
#     await inline_query.answer(results, cache_time=0, is_personal=True)
#
# @router.inline_query(F.query.startswith("photo"))
# async def show_user_gifs(inline_query: InlineQuery):
#     results = []
#
#     search_text = inline_query.query.replace("photo", "").strip()
#
#     meme_list = await get_memes(search_text, "photo", str(inline_query.from_user.id))
#     logger.info(meme_list)
#     for meme in meme_list:
#         results.append(InlineQueryResultCachedPhoto(
#             title=meme.name,
#             photo_file_id=meme.file_id,
#             id=str(meme.id)
#        ))
#     await inline_query.answer(results, cache_time=0, is_personal=True)



@router.inline_query(F.query.startswith("http"))
async def download_link(inline_query: InlineQuery):
    
    ...


@router.inline_query()
async def show_all_memes(inline_query: InlineQuery):
    results = []


    search_text = inline_query.query.strip()

    start_time = datetime.now()
    meme_list = await get_memes(search_text, "*", str(inline_query.from_user.id))
    end_time = datetime.now()

    for meme in meme_list:
        match meme.mime_type:
             case "video":
                 results.append(InlineQueryResultCachedVideo(
                     title=meme.name,
                     video_file_id=meme.file_id,
                     id=str(meme.id)
                 ))
             case "audio":
                 results.append(InlineQueryResultCachedDocument(
                     title=meme.name,
                     document_file_id=meme.file_id,
                     id=str(meme.id)
                 ))
             case "sticker":
                 results.append(InlineQueryResultCachedSticker(
                     sticker_file_id=meme.file_id,
                     title=meme.name,
                     id=str(meme.id)
                 ))
             case "gif":
                 results.append(InlineQueryResultCachedGif(
                     gif_file_id=meme.file_id,
                     title=meme.name,
                     id=str(meme.id)
                 ))
             case "photo":
                 results.append(InlineQueryResultCachedPhoto(
                     photo_file_id=meme.file_id,
                     title=meme.name,
                     id=str(meme.id)
                 ))

    await inline_query.answer(results, cache_time=0, is_personal=True)
    await bot.send_message(inline_query.from_user.id, str(end_time - start_time))