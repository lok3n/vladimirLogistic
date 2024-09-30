from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from utils.keyboards import menu_kb

menu_router = Router()


@menu_router.callback_query(F.data == 'show_menu')
async def show_menu_handler(callback: CallbackQuery):
    await callback.message.edit_text('Здесь Вы можете перейти в специальные каналы',
                                     reply_markup=menu_kb())


@menu_router.callback_query(F.data == "numbers")
async def sklad_handler(callback: CallbackQuery):
    await callback.answer('В разработке', show_alert=True)
