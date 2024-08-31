from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup


def registration_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder().button(text='🔑 Регистрация', callback_data='registration').as_markup()


def change_status_kb(status) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if status == 0:
        builder.button(text='🏬 Нахожусь на РЦ', callback_data='change_status')
        builder.button(text='📝 Сменить данные', callback_data='registration')
    elif status == 1:
        builder.button(text='🚚 Я в рейсе', callback_data='change_status')
    elif status == 2:
        builder.button(text='✅ Закончил рейс', callback_data='change_status')
    return builder.adjust(1).as_markup()


def back_btn(callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder().button(text='↩️ Назад', callback_data=callback).as_markup()


def write_btn(user_id: int) -> InlineKeyboardMarkup | None:
    try:
        return InlineKeyboardBuilder().button(text='👤 Написать', url=f'tg://user?id={user_id}').as_markup()
    except:
        return None
