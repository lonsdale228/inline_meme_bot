from aiogram import F, Router
from aiogram.types import InlineQuery, InlineQueryResultCachedVideo, InlineQueryResultCachedDocument, \
    InlineQueryResultCachedSticker, InlineQueryResultCachedGif, InlineQueryResultCachedPhoto

from database.models import Meme
from database.utils import get_memes

router = Router()


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


@router.inline_query()
async def show_all_memes(inline_query: InlineQuery):
    results = []


    search_text = inline_query.query.strip()

    meme_list = await get_memes(search_text, "*", str(inline_query.from_user.id))

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