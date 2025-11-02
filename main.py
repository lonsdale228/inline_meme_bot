import asyncio

from aiogram import Dispatcher

from handlers.inline_mode import router as inline_router
from handlers.start import router as start_router
from handlers.saving_meme import router as saving_meme_router
from handlers.user import router as user_router
from handlers.add_to_groups import router as add_to_groups_router
from handlers.inline_downloader import router as inline_downloader
from database.connection import sessionmanager
from database.models import Base
import loader
from scheduler import setup_scheduler

dp = Dispatcher()
dp.include_routers(
    inline_downloader,
    inline_router,
    start_router,
    saving_meme_router,
    user_router,
    add_to_groups_router,
)


async def main():
    async with sessionmanager.connect() as connection:
        await connection.run_sync(Base.registry.configure)
        await connection.run_sync(Base.metadata.create_all)
    await setup_scheduler()
    await dp.start_polling(loader.bot)


if __name__ == "__main__":
    asyncio.run(main())