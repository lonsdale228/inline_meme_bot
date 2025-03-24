
from aiogram import F, Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultVideo, \
    InlineQueryResultCachedVideo, InlineQueryResultCachedAudio, InlineQueryResultCachedDocument, InlineQueryResultCachedSticker, InlineQueryResultCachedGif

from database.connection import get_session
from database.models import Meme
from database.utils import get_memes
from loader import logger

router = Router()



@router.inline_query(F.query=="")
async def show_possible_commands(inline_query: InlineQuery):
    results = []

    available_commands = {
        "meme": "Show video meme",
        "ameme": "Show audio meme",
        "gif": "Show gif",
        "st": "Show stickers",
    }


    for i, (command, desc) in enumerate(available_commands.items()):
        results.append(
            InlineQueryResultArticle(
                id = str(i),
                title = command,
                description = desc,
                input_message_content = InputTextMessageContent(
                    message_text="it just a hint, dont click on it",
                ),
            )
        )
    await inline_query.answer(results, cache_time=0, is_personal=True)



@router.inline_query(F.query.startswith("meme"))
async def show_user_videos(inline_query: InlineQuery):
    results = []

    search_text = inline_query.query.replace("meme", "").strip()

    meme_list = await get_memes(search_text, "video")
    logger.info(meme_list)
    for meme in meme_list:
        results.append(InlineQueryResultCachedVideo(
            title=meme.title,
            video_file_id=meme.file_id,
            description=meme.description,
            id=str(meme.id)
       ))
    await inline_query.answer(results, cache_time=0, is_personal=True)



@router.inline_query(F.query.startswith("ameme"))
async def show_user_audios(inline_query: InlineQuery):
    results = []

    search_text = inline_query.query.replace("ameme", "").strip()

    meme_list = await get_memes(search_text, "audio")
    logger.info(meme_list)
    for meme in meme_list:
        results.append(InlineQueryResultCachedDocument(
            caption=meme.title,
            title=meme.title,
            document_file_id=meme.file_id,
            description=meme.title,
            id=str(meme.id)
       ))
    await inline_query.answer(results, cache_time=0, is_personal=True)



@router.inline_query(F.query.startswith("st"))
async def show_user_stickers(inline_query: InlineQuery):
    results = []

    search_text = inline_query.query.replace("st", "").strip()

    meme_list = await get_memes(search_text, "sticker")
    logger.info(meme_list)
    for meme in meme_list:
        results.append(InlineQueryResultCachedSticker(
            title=meme.title,
            sticker_file_id=meme.file_id,
            id=str(meme.id)
       ))
    await inline_query.answer(results, cache_time=0, is_personal=True)


@router.inline_query(F.query.startswith("gif"))
async def show_user_gifs(inline_query: InlineQuery):
    results = []

    search_text = inline_query.query.replace("gif", "").strip()

    meme_list = await get_memes(search_text, "gif")
    logger.info(meme_list)
    for meme in meme_list:
        results.append(InlineQueryResultCachedGif(
            title=meme.title,
            gif_file_id=meme.file_id,
            id=str(meme.id)
       ))
    await inline_query.answer(results, cache_time=0, is_personal=True)




