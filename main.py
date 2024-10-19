import datetime
import os
import sys
from asyncio import run
from os import getenv
from logging import basicConfig, INFO
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand
from handlers import *
from utils.models import Users, Races

load_dotenv()
bot = Bot(token=getenv('BOT_TOKEN'))
dp = Dispatcher()
scheduler = AsyncIOScheduler()
dp.include_routers(start_router, registration_router, change_status_router, cancel_race_router,
                   menu_router, admin_router)


async def main():
    tables = [Users, Races]
    for table in tables:
        if not table.table_exists():
            table.create_table()

    print('started')
    basicConfig(filename='logs.log', level=INFO)
    # basicConfig(level=INFO, stream=sys.stdout)
    await bot.set_my_commands([BotCommand(command='start', description='Главное меню')])
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    run(main())
