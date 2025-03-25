import asyncio

from database.connection import sessionmanager
from database.models import Base
from loader import dp, bot


async def main():
    async with sessionmanager.connect() as connection:
        await connection.run_sync(Base.metadata.create_all)
    await dp.start_polling(bot)



if __name__ == '__main__':
    asyncio.run(main())