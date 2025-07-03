import uuid

from aiofiles import os
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, FSInputFile, InputMediaVideo, \
    ChosenInlineResult, InlineKeyboardMarkup, InlineKeyboardButton, Message
from loader import bot, logger
import subprocess

router = Router()

async def dl_video_task(url: str, unique_file_id: str | int):
    YT_DLP_PATH = await os.path.abspath("yt-dlp")
    YT_DLP_COOKIES = await os.path.abspath("yt-dlp-cookies.txt")
    subprocess.call([
        YT_DLP_PATH,
        "-o", f"{unique_file_id}.mp4",
        "-f", "b[filesize<49M]/w",
        "--force-overwrite",
        "--cookies", YT_DLP_COOKIES,
        "--postprocessor-args", "-movflags +faststart",
        url
    ])


async def download_video(url: str, unique_file_id: str | int, inline_msg_id, file_format: str | None = None):
    YT_DLP_PATH = await os.path.abspath("yt-dlp")
    YT_DLP_COOKIES = await os.path.abspath("yt-dlp-cookies.txt")
    file_extension = file_format or 'mp4'
    cmd = [
        YT_DLP_PATH,
        "-o", f"{unique_file_id}.{file_extension}",
        "-f", "b[filesize<49M]/w",
        "--force-overwrite",
        "--no-playlist",
        "--cookies", YT_DLP_COOKIES,
        "--postprocessor-args", "-movflags +faststart",
        url
    ]

    if file_format:
        cmd.extend(["--audio-format", file_format])

    subprocess.call(cmd)

    filename = await os.path.abspath(f"{unique_file_id}.{file_extension}")
    logger.info(f"File path: {filename}")
    if await os.path.exists(filename):

        video = FSInputFile(path=filename)

        msg_vid = await bot.send_video(chat_id=-4601538575, video=video)



        logger.info(f"Inline msg id: {inline_msg_id}")
        await bot.edit_message_media(
            media=InputMediaVideo(media=msg_vid.video.file_id),
            inline_message_id=inline_msg_id,
        )
        await os.remove(filename)

@router.inline_query(F.query.contains('https'))
async def inline_downloader(inline_query: InlineQuery):
    results = [
        InlineQueryResultArticle(
            id=str(inline_query.id),
            title='Click here to download video!',
            input_message_content=InputTextMessageContent(
                message_text="Downloading..."
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Downloading...", callback_data=str(uuid.uuid4()))]
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
    url, sep, file_format = chosen_result.query.strip().partition(" ")

    await download_video(url=url, unique_file_id=str(chosen_result.from_user.id),
                         inline_msg_id=inline_msg_id, file_format=file_format or None)


@router.message(Command('update'))
async def update_handler(message: Message):
    YT_DLP_PATH = await os.path.abspath("yt-dlp")
    await message.answer("Started updating yt-dlp...")
    subprocess.call([
        YT_DLP_PATH,
        "--update-to", "nightly"
    ])
    await message.answer("Updating finished!")

