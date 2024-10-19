import datetime
import os
from aiogram import Bot
from utils.models import Users


async def send_report_drivers(bot: Bot):
    for i in range(5):
        text = await format_text(i)
        if text is not None:
            await bot.send_message(chat_id=os.getenv('CHANNEL_ID'), text=text, parse_mode="HTML")


async def format_text(driver_status: int):
    titles = ['Не на смене', 'Ждут погрузки', 'Едут на РЦ', 'В рейсе', 'Разгружается на точке']
    text, users = '', []
    link = f'https://t.me/c/{os.getenv("CHANNEL_ID").lstrip("-100")}'

    if driver_status == 0:
        delta = datetime.timedelta(days=1)
        for user in Users.select().where(Users.status == 0):
            if user.datetime_cancel and user.datetime_cancel + delta > datetime.datetime.now():
                users.append(user)
    elif driver_status:
        users: list[Users] = Users.select().where(Users.status == driver_status)

    for user in users:
        points = f', осталось {user.points - user.points_done} точек' if driver_status == 3 or driver_status == 4 else ''
        text += f'<b>{user.number_car}</b> <a href="{link}/{user.notify_msg_id}"><i>{user.fullname}</i></a>{points}\n'
    return f'<b>{titles[driver_status]}</b>\n{text}' if users else None
