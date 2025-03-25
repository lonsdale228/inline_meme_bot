import asyncio
import os

from aiogram import Dispatcher, Bot

from handlers.inline_mode import router as r1
from handlers.start import router as r3
from handlers.saving_images import router as image_router
from handlers.user import router as user_router
from handlers.add_to_groups import router as add_to_groups_router
from database.connection import sessionmanager
from database.models import Base
import loader



dp = Dispatcher()
dp.include_routers(r1,r3,image_router,user_router,add_to_groups_router)





async def main():
    async with sessionmanager.connect() as connection:
        await connection.run_sync(Base.metadata.create_all)
    await dp.start_polling(loader.bot)



if __name__ == '__main__':
    asyncio.run(main())