import logging
import os
import sys

from aiogram import Bot

logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO,
    stream=sys.stdout
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("HELLO!")
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(BOT_TOKEN)