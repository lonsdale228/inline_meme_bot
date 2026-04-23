import json
import secrets
import uuid

import aiofiles
import aiohttp
from aiofiles import os
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    FSInputFile,
    InputMediaVideo,
    InputMediaAudio,
    ChosenInlineResult,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)
from loader import bot, logger
from asyncio import subprocess

from utils.time_parsing import parse_text
from utils.yt_dlp_utils import update_ytdlp

router = Router()

AUDIO_FORMATS = {"mp3", "m4a", "opus", "aac", "flac", "wav", "vorbis"}


async def fetch_metadata(url: str, cookies_path: str, yt_dlp_path: str):
    try:
        task = await subprocess.create_subprocess_exec(
            yt_dlp_path,
            "--no-playlist",
            "--cookies",
            cookies_path,
            "-J",
            url,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, _ = await task.communicate()
        if task.returncode != 0 or not stdout:
            return None, None

        info = json.loads(stdout)
        title = info.get("track") or info.get("title")
        performer = info.get("artist") or info.get("uploader")
        return title, performer
    except Exception as e:
        logger.warning(f"Could not fetch metadata: {e}")
        return None, None


async def dl_video_task(url: str, section):
    YT_DLP_PATH = await os.path.abspath("yt-dlp")
    YT_DLP_COOKIES = await os.path.abspath("yt-dlp-cookies.txt")
    temp_name = secrets.token_hex(4)
    task = await subprocess.create_subprocess_exec(
        YT_DLP_PATH,
        "--download-sections",
        section,
        "--force-keyframes-at-cuts",
        "-o",
        f"{temp_name}.mp4",
        "-f",
        "b[filesize<49M]/best",
        "--force-overwrite",
        "--cookies",
        YT_DLP_COOKIES,
        url,
    )
    returncode = await task.wait()
    logger.info(f"Return code: {returncode}")
    return temp_name

async def download_tiktok_fast(url: str, output_path: str) -> bool:
    """Download TikTok video via tikwm API. Returns True on success."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://tikwm.com/api/",
                data={"url": url, "hd": 1},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as r:
                data = await r.json()

            if data.get("code") != 0 or not data.get("data"):
                logger.warning(f"tikwm returned no data: {data}")
                return False

            video_url = data["data"].get("hdplay") or data["data"].get("play")
            if not video_url:
                return False

            async with session.get(video_url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status != 200:
                    return False
                async with aiofiles.open(output_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(8192):
                        await f.write(chunk)

        return await os.path.exists(output_path)
    except Exception as e:
        logger.warning(f"tikwm fast download failed: {e}")
        return False

async def extract_tiktok_audio(video_path: str, audio_path: str, audio_format: str) -> bool:
    """Extract audio from downloaded mp4 using ffmpeg."""
    try:
        task = await subprocess.create_subprocess_exec(
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "libmp3lame" if audio_format == "mp3" else "copy",
            audio_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        await task.wait()
        return task.returncode == 0 and await os.path.exists(audio_path)
    except Exception as e:
        logger.warning(f"ffmpeg audio extract failed: {e}")
        return False

async def download_video(
    url: str,
    unique_file_id: str | int,
    inline_msg_id,
    file_format: str | None = None,
):
    YT_DLP_PATH = await os.path.abspath("yt-dlp")
    YT_DLP_COOKIES = await os.path.abspath("yt-dlp-cookies.txt")

    is_audio = file_format is not None and file_format.lower() in AUDIO_FORMATS
    final_ext = file_format if is_audio else "mp4"
    filename = await os.path.abspath(f"{unique_file_id}.{final_ext}")

    # --- FAST PATH: TikTok via tikwm ---
    fast_success = False
    if "tiktok.com" in url.lower():
        mp4_path = await os.path.abspath(f"{unique_file_id}.mp4")
        logger.info("Trying tikwm fast path for TikTok...")
        if await download_tiktok_fast(url, mp4_path):
            if is_audio:
                # extract audio from the mp4, then remove the mp4
                if await extract_tiktok_audio(mp4_path, filename, file_format):
                    fast_success = True
                if await os.path.exists(mp4_path) and mp4_path != filename:
                    await os.remove(mp4_path)
            else:
                fast_success = True
            logger.info(f"tikwm fast path success: {fast_success}")

    # --- FALLBACK: yt-dlp ---
    if not fast_success:
        output_template = f"{unique_file_id}.%(ext)s"
        cmd = [
            YT_DLP_PATH,
            "-o", output_template,
            "--force-overwrite",
            "--no-playlist",
            "--cookies", YT_DLP_COOKIES,
        ]

        if is_audio:
            cmd += ["-f", "bestaudio", "-x", "--audio-format", file_format, "--add-metadata"]
        else:
            cmd += ["-f", "b[filesize<49M]/best", "--remux-video", "mp4"]

        cmd.append(url)
        logger.info(cmd)

        task = await subprocess.create_subprocess_exec(*cmd)
        returncode = await task.wait()
        logger.info(f"yt-dlp return code: {returncode}")

    logger.info(f"File path: {filename}")

    if not await os.path.exists(filename):
        logger.error(f"Expected output file not found: {filename}")
        return
    try:
        input_file = FSInputFile(path=filename)

        if is_audio:
            title, performer = await fetch_metadata(url, YT_DLP_COOKIES, YT_DLP_PATH)
            logger.info(f"Audio metadata: title={title!r}, performer={performer!r}")

            msg = await bot.send_audio(
                chat_id=-4601538575,
                audio=input_file,
                title=title,
                performer=performer,
            )
            logger.info(f"Inline msg id: {inline_msg_id}")
            await bot.edit_message_media(
                media=InputMediaAudio(
                    media=msg.audio.file_id,
                    title=title,
                    performer=performer,
                ),
                inline_message_id=inline_msg_id,
            )
        else:
            msg = await bot.send_video(
                chat_id=-4601538575,
                video=input_file,
            )
            logger.info(f"Inline msg id: {inline_msg_id}")
            await bot.edit_message_media(
                media=InputMediaVideo(media=msg.video.file_id),
                inline_message_id=inline_msg_id,
            )

    except Exception as e:
        logger.error(e, exc_info=True)

    finally:
        if await os.path.exists(filename):
            await os.remove(filename)


@router.inline_query(F.query.contains("tiktok.com"))
async def inline_tiktok_downloader(inline_query: InlineQuery):
    results = [
        InlineQueryResultArticle(
            id=str(inline_query.id),
            title="Click here to download video!",
            input_message_content=InputTextMessageContent(
                message_text="Downloading..."
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Downloading...", callback_data=str(uuid.uuid4())
                        )
                    ]
                ]
            ),
        )
    ]

    await inline_query.answer(results, cache_time=0, is_personal=True)

@router.inline_query(F.query.contains("https"))
async def inline_downloader(inline_query: InlineQuery):
    results = [
        InlineQueryResultArticle(
            id=str(inline_query.id),
            title="Click here to download video!",
            input_message_content=InputTextMessageContent(
                message_text="Downloading..."
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Downloading...", callback_data=str(uuid.uuid4())
                        )
                    ]
                ]
            ),
        )
    ]

    await inline_query.answer(results, cache_time=0, is_personal=True)


class GetMemeName(StatesGroup):
    meme_name = State()


@router.message(F.text.contains("https"), StateFilter("*"))
async def message_downloader(message: Message, state: FSMContext):
    text = message.text

    parsed_list = parse_text(text)
    if not parsed_list:
        raise ValueError("No downloadable items found in text")

    p = parsed_list[0]

    url = p["url"]
    section = p["section"]
    logger.info(f"Downloading meme from {url} with section {section}")
    filename = await dl_video_task(url, section)

    logger.info(f"Filename: {filename}")
    video_file = FSInputFile(filename + ".mp4")
    video_msg = await message.answer_video(video_file, caption="Enter meme keywords!")

    await state.update_data(meme_unique_file_id=video_msg.video.file_unique_id)
    await state.update_data(meme_file_id=video_msg.video.file_id)

    await state.set_state(GetMemeName.meme_name)


@router.chosen_inline_result()
async def chosen_inline_result_query(chosen_result: ChosenInlineResult):
    inline_msg_id: str = chosen_result.inline_message_id
    url, sep, file_format = chosen_result.query.strip().partition(" ")

    file_format = file_format.strip().lower() or None

    await download_video(
        url=url,
        unique_file_id=str(chosen_result.from_user.id),
        inline_msg_id=inline_msg_id,
        file_format=file_format,
    )


@router.message(Command("update"))
async def update_handler(message: Message):
    await message.answer("Started updating yt-dlp...")
    await update_ytdlp()
    await message.answer("Updating finished!")