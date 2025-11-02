from asyncio import subprocess

from aiofiles import os


async def update_ytdlp():
    YT_DLP_PATH = await os.path.abspath("yt-dlp")
    await subprocess.create_subprocess_exec(YT_DLP_PATH, "--update-to", "nightly")
    