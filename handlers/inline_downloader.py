import uuid
from mailbox import Message

from aiofiles import os
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, FSInputFile, InputMediaVideo, \
    ChosenInlineResult, InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot, logger
import subprocess

router = Router()


async def install_ytdlp():
    ...


async def download_video(url: str, unique_file_id: str | int, inline_msg_id):
    YT_DLP_PATH = await os.path.abspath("yt-dlp")
    subprocess.call([
        YT_DLP_PATH,
        "-o", f"{unique_file_id}.mp4",
        "-f", "b[filesize<49M]/w",
        "--force-overwrite",
        url
    ])

    filename = await os.path.abspath(f"{unique_file_id}.mp4")
    logger.info(f"File path: {filename}")
    if await os.path.exists(filename):

        video = FSInputFile(path=filename)

        msg_vid = await bot.send_video(chat_id=-4601538575, video=video)



        logger.info(f"Inline msg id: {inline_msg_id}")
        await bot.edit_message_media(
            media=InputMediaVideo(media=msg_vid.video.file_id),
            inline_message_id=inline_msg_id,
        )


@router.inline_query(F.query.contains('https'))
async def inline_downloader(inline_query: InlineQuery):
    results = [
        InlineQueryResultArticle(
            id=str(inline_query.id),
            title='Click here to download video!',
            input_message_content=InputTextMessageContent(
                message_text="Wait..."
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Please wait...", callback_data=str(uuid.uuid4()))]
                ])
        )
    ]

    await inline_query.answer(
        results,
        cache_time=0,
        is_personal=True
    )


@router.chosen_inline_result()
async def chosen_inline_result_query(chosen_result: ChosenInlineResult):
    inline_msg_id: str = chosen_result.inline_message_id
    inline_query = chosen_result.query.strip()

    await download_video(url=inline_query, unique_file_id=str(chosen_result.from_user.id),
                         inline_msg_id=inline_msg_id)


@router.message(Command('update'))
async def update_handler(message: Message):
    YT_DLP_PATH = await os.path.abspath("yt-dlp")
    subprocess.call([
        YT_DLP_PATH,
        "--update-to", "nightly"
    ])
