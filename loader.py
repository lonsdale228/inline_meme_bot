import logging
import os

from handlers.inline_mode import router as r1
from handlers.start import router as r3
from handlers.saving_images import router as image_router
from handlers.user import router as user_router
from handlers.add_to_groups import router as add_to_groups_router

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(BOT_TOKEN)

dp = Dispatcher()
dp.include_routers(r1,r3,image_router,user_router,add_to_groups_router)