from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup


def registration_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder().button(text='🔑 Регистрация', callback_data='registration').as_markup()


def change_status_kb(status) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if not status:
        builder.button(text='🚀 Начать смену', callback_data='change_status')
        builder.button(text='📝 Сменить данные', callback_data='registration')
    elif status == 1:
        builder.button(text='🏬 Нахожусь на РЦ', callback_data='change_status')
    elif status == 2:
        builder.button(text='🚚 Начать рейс', callback_data='change_status')
    elif status == 3:
        builder.button(text='📦 Выгружаюсь', callback_data='change_status')
    elif status == 4:
        builder.button(text='🚚 Продолжить рейс', callback_data='change_status')
    builder.button(text='ℹ️ Информация', callback_data='show_menu')
    return builder.adjust(1).as_markup()


def cancel_or_continue() -> InlineKeyboardMarkup:
    return (InlineKeyboardBuilder().
            button(text='🚚 Еду на РЦ', callback_data='continue_race').
            button(text='🚚 Построить маршрут до РЦ',
                   url='https://yandex.ru/navi?whatshere%5Bpoint%5D=37.429608104937564%2C55.69606885085871&whatshere%5Bzoom%5D=16.501898&ll=37.42972409487407%2C55.69609284419613&z=16.501898').
            button(text='🚩 Закончить смену', callback_data='cancel_race').adjust(1).as_markup())


def next_btn(callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder().button(text='⏩ Далее', callback_data=callback).as_markup()


def back_btn(callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder().button(text='↩️ Назад', callback_data=callback).as_markup()


def goto_btn(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder().button(text='🌐 Перейти', url=url).as_markup()


def write_btn(user_id: int) -> InlineKeyboardMarkup | None:
    try:
        return InlineKeyboardBuilder().button(text='👤 Написать', url=f'tg://user?id={user_id}').as_markup()
    except:
        return None


def send_location() -> ReplyKeyboardMarkup:
    return (ReplyKeyboardBuilder().
            button(text='Отправить локацию', request_location=True).
            button(text='Назад').
            adjust(1).as_markup(resize_keyboard=True, one_time_keyboard=True))


def menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='Дежурные номера', callback_data='numbers')
    builder.button(text='Справочник', url='https://t.me/+KAhSU_pavW8zOWUy')
    builder.button(text='Общий чат (наёмники)', url='https://t.me/+kVoHpwiKeDsyMWQy')
    builder.button(text='Общий чат (собственный ТС)', url='https://t.me/+PS69_7ywbjg5YTVi')
    builder.button(text='🚚 Построить маршрут до РЦ',
                   url='https://yandex.ru/navi?whatshere%5Bpoint%5D=37.429608104937564%2C55.69606885085871&whatshere%5Bzoom%5D=16.501898&ll=37.42972409487407%2C55.69609284419613&z=16.501898')
    builder.button(text='↩️ Назад', callback_data='start')
    return builder.adjust(1).as_markup()
