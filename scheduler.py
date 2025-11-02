import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from utils.yt_dlp_utils import update_ytdlp


async def setup_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_ytdlp, trigger=CronTrigger(hour=4))
    scheduler.start()
    logging.info("Scheduler started")