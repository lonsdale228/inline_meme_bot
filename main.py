import asyncio
import os

from aiogram import Dispatcher, Bot

from handlers.inline_mode import router as r1
from handlers.saving_video import router as r2
from handlers.start import router as r3
from handlers.saving_images import router as image_router
from handlers.user import router as user_router
from database.connection import sessionmanager
from database.models import Base
import loader

BOT_TOKEN = os.getenv('BOT_TOKEN')


dp = Dispatcher()
dp.include_routers(r1,r2,r3,image_router,user_router)

bot = Bot(BOT_TOKEN)




async def main():
    async with sessionmanager.connect() as connection:
        await connection.run_sync(Base.metadata.create_all)
    await dp.start_polling(bot)



if __name__ == '__main__':
    asyncio.run(main())