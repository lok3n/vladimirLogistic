import datetime
import os
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from functions import send_report_drivers, create_excel
from utils.models import Races
from utils.states import AdminStates

admin_router = Router()


@admin_router.message(Command('update'))
async def update_handler(message: Message):
    member = await message.bot.get_chat_member(os.getenv('CHANNEL_ID'), message.from_user.id)
    if member.status in ["member", "administrator", "creator"]:
        await send_report_drivers(message.bot)
        await message.answer('✅ Сводка отправлена в канал!')


@admin_router.message(Command('statistic'))
async def update_handler(message: Message, state: FSMContext):
    member = await message.bot.get_chat_member(os.getenv('CHANNEL_ID'), message.from_user.id)
    if member.status in ["member", "administrator", "creator"]:
        await state.set_state(AdminStates.input_from_date)
        await message.answer('Укажите дату от которой необходима выгрузка в формате дд.мм.гг')


@admin_router.message(AdminStates.input_from_date)
async def input_from_date(message: Message, state: FSMContext):
    try:
        date = datetime.datetime.strptime(message.text, '%d.%m.%y')
    except:
        return await message.answer('Ошибка! Введите дату в формате дд.мм.гг')
    await state.set_state(AdminStates.input_to_date)
    await state.update_data(from_date=date)
    await message.answer('Введите дату до которой необходима выгрузка, в формате дд.мм.гг')


@admin_router.message(AdminStates.input_to_date)
async def input_from_date(message: Message, state: FSMContext):
    try:
        to_date = datetime.datetime.combine(datetime.datetime.strptime(message.text, '%d.%m.%y').date(),
                                            datetime.time(23, 59, 59, 999999))
    except:
        return await message.answer('Ошибка! Введите дату в формате дд.мм.гг')
    data = await state.get_data()
    await state.clear()
    await create_excel(Races.select().where(Races.datetime_start.between(data.get('from_date'), to_date)),
                       file_name=f'{data.get("from_date").day}-{to_date.day}')
    await message.answer_document(document=FSInputFile(f'excel_files/{data.get("from_date").day}-{to_date.day}.xlsx'),
                                  caption='✅ Статистика за выбранный период выгружена!')
