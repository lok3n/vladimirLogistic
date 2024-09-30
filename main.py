import sys
from asyncio import run
from os import getenv
from logging import basicConfig, INFO
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand
from handlers import *
from functions import send_report_drivers
from utils.models import Users

load_dotenv()
bot = Bot(token=getenv('BOT_TOKEN'))
dp = Dispatcher()
scheduler = AsyncIOScheduler()
dp.include_routers(start_router, registration_router, change_status_router, cancel_race_router,
                   menu_router)


async def main():
    if not Users.table_exists():
        Users.create_table()

    await send_report_drivers(bot)
    print('started')
    basicConfig(filename='logs.log', level=INFO)
    # basicConfig(level=INFO, stream=sys.stdout)
    await bot.set_my_commands([BotCommand(command='start', description='Главное меню'),
                               BotCommand(command='sklad', description='Сборник ДСов фото/адреса'),
                               BotCommand(command='numbers', description='Дежурные номера Дарк Сторов'),
                               BotCommand(command='chat', description='Общий чат')])
    scheduler.add_job(send_report_drivers, 'cron', hour='*/2', kwargs={'bot': bot})
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    run(main())
