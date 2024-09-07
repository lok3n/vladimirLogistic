import os

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from utils.models import Users
from utils.keyboards import registration_kb, change_status_kb, goto_btn

start_router = Router()


@start_router.callback_query(F.data == 'start')
@start_router.message(Command('start'))
async def start_handler(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    user = Users.get_or_none(Users.user_id == event.from_user.id)
    func = event.answer if isinstance(event, Message) else event.message.edit_text

    if not user:
        return await func(f'<b>👋 Приветствую, {event.from_user.first_name}!</b>\n\n'
                          f'🤖 Я - бот для контроля статусов водителей\n\n'
                          f'Для начала пользования ботом, необходимо пройти регистрацию',
                          reply_markup=registration_kb(), parse_mode="HTML")
    else:
        status = ['В пути на РЦ', 'Нахожусь на РЦ', 'В рейсе', 'Разгружаюсь на точке']
        await func(f'<b>👋 Приветствую, {event.from_user.first_name}!</b>\n\n'
                   f'🤖 Я - бот для контроля статусов водителей\n\n'
                   f'👉 <b>Ваш текущий статус: {status[user.status]}</b>\n\n'
                   f'<i>Чтобы сменить статус, нажмите на кнопку ниже</i> 👇', reply_markup=change_status_kb(user.status),
                   parse_mode="HTML")


@start_router.message(Command('admin'))
async def admin_handle(message: Message):
    url = await message.bot.create_chat_invite_link(os.getenv('CHANNEL_ID'), member_limit=1)
    await message.answer('Admin channel', reply_markup=goto_btn(url.invite_link))
