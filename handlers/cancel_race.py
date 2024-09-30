import datetime
import os

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from utils.states import ChangeStatus
from utils.keyboards import send_location
from utils.models import Users
from handlers.start import start_handler

cancel_race_router = Router()


@cancel_race_router.callback_query(F.data == 'cancel_race')
async def cancel_race_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        'ℹ️ Вы хотите закончить свою смену, для этого отправьте свою геолокацию нажав на соответсвующую кнопку снизу',
        reply_markup=send_location())
    await state.set_state(ChangeStatus.send_location_cancel)


@cancel_race_router.message(ChangeStatus.send_location_cancel, F.location)
async def handle_location(message: Message, state: FSMContext):
    user: Users = Users.get_or_none(Users.user_id == message.from_user.id)
    user.status = 0
    text = f'''Водитель <i>{user.fullname}</i> с номером ТС <i>{user.number_car}</i> закончил смену
Координаты: <code>{message.location.latitude}, {message.location.longitude}</code>'''
    notify_msg = await message.bot.send_message(os.getenv('CHANNEL_ID'), text, parse_mode="HTML")
    await message.bot.send_location(os.getenv('CHANNEL_ID'),
                                    latitude=message.location.latitude,
                                    longitude=message.location.longitude)
    user.notify_msg_id = notify_msg.message_id
    user.datetime_cancel = datetime.datetime.now()
    user.save()
    await start_handler(message, state)


@cancel_race_router.message(F.text, ChangeStatus.send_location_cancel)
async def handle_message(message: Message, state: FSMContext):
    if message.text != 'Назад':
        await message.answer('Ошибка! Отправьте локацию или нажмите назад')
    else:
        await start_handler(message, state)
