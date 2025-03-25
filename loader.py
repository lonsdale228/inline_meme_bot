import logging
import os

from aiogram import Bot

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(BOT_TOKEN)