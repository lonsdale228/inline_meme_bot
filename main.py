import asyncio
import os

from aiogram import Dispatcher, Bot

from handlers.inline_mode import router as inline_router
from handlers.start import router as start_router
from handlers.saving_meme import router as saving_meme_router
from handlers.user import router as user_router
from handlers.add_to_groups import router as add_to_groups_router
from database.connection import sessionmanager
from database.models import Base
import loader



dp = Dispatcher()
dp.include_routers(inline_router,start_router,saving_meme_router,user_router,add_to_groups_router)





async def main():
    async with sessionmanager.connect() as connection:
        await connection.run_sync(Base.registry.configure)
        await connection.run_sync(Base.metadata.create_all)
    await dp.start_polling(loader.bot)



if __name__ == '__main__':
    asyncio.run(main())