import os
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from utils.models import Users
from utils.keyboards import write_btn, back_btn, next_btn
from utils.states import ChangeStatus

change_status_router = Router()


@change_status_router.callback_query(F.data == 'change_status')
async def change_status_handler(callback: CallbackQuery, state: FSMContext):
    user: Users = Users.get_or_none(Users.user_id == callback.from_user.id)
    await state.clear()

    if user.status == 0:
        user.status = 1
        user.save()
        text = f'Водитель <i>{user.fullname}</i> с номером ТС <i>{user.number_car}</i> ждёт погрузки'
        await callback.bot.send_message(os.getenv('CHANNEL_ID'), text, reply_markup=write_btn(user.user_id),
                                        parse_mode="HTML")
        await callback.message.edit_text('✅ Вы сменили свой статус на <i>«Нахожусь на РЦ»</i>',
                                         reply_markup=next_btn('start'), parse_mode="HTML")

    elif user.status == 1:
        text = 'ℹ️ Введите количество точек выгрузки'
        await state.set_state(ChangeStatus.input_points)
        await state.update_data(past_msg_id=callback.message.message_id)
        await callback.message.edit_text(text, reply_markup=back_btn('start'))

    if user.status == 2:
        user.status = 3
        user.points_done += 1
        user.save()
        text = (f'Водитель <i>{user.fullname}</i> с номером ТС <i>{user.number_car}</i> выгружается на '
                f'<i>{user.points_done}</i> точке, ещё <i>{user.points - user.points_done}</i> точек')
        await callback.bot.send_message(os.getenv('CHANNEL_ID'), text, reply_markup=write_btn(user.user_id),
                                        parse_mode="HTML")
        await callback.message.edit_text(f'✅ Вы сменили свой статус на <i>«Выгружаюсь»</i>\n📍 Текущая точка: '
                                         f'<i>{user.points_done}</i>, осталось <i>{user.points - user.points_done}</i>'
                                         f' точек',
                                         reply_markup=next_btn('start'), parse_mode="HTML")

    elif user.status == 3:
        if user.points_done >= user.points:
            text = 'ℹ️ Введите сколько времени показывает по навигатору до РЦ'
            await state.set_state(ChangeStatus.input_time_to_base)
            await state.update_data(past_msg_id=callback.message.message_id)
            await callback.message.edit_text(text, reply_markup=back_btn('start'))
        else:
            user.status = 2
            user.save()
            text = f'Водитель <i>{user.fullname}</i> с номером ТС <i>{user.number_car}</i> продолжает маршрут'
            await callback.bot.send_message(os.getenv('CHANNEL_ID'), text, reply_markup=write_btn(user.user_id),
                                            parse_mode="HTML")
            await callback.message.edit_text(f'✅ Вы сменили свой статус на <i>«В рейсе»</i>, езжайте на следующую'
                                             f' точку', reply_markup=next_btn('start'), parse_mode="HTML")


@change_status_router.message(ChangeStatus.input_points)
async def input_points_handler(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    if not message.text.isdigit():
        return await message.bot.edit_message_text('❌ Ошибка! Можно ввести только цифры\n'
                                                   'ℹ️ Введите количество точек выгрузки',
                                                   reply_markup=next_btn('start'), chat_id=message.chat.id,
                                                   message_id=data['past_msg_id'], parse_mode="HTML")

    user: Users = Users.get_or_none(Users.user_id == message.from_user.id)
    user.status = 2
    user.points = int(message.text)
    user.save()
    text = (f'✅ Вы сменили свой статус на <i>«В рейсе»</i>\n'
            f'📍 Количество точек выгрузки: <i>{message.text} точек</i>\n\n'
            f'👍 Желаем вам приятной дороги\n'
            f'ℹ️ После завершения рейса, не забудьте сменить свой статус!')

    notify_text = f'Водитель <i>{user.fullname}</i> с номером ТС <i>{user.number_car}</i> загрузился на <i>{message.text}</i> точек'
    await state.clear()

    await message.bot.send_message(os.getenv('CHANNEL_ID'), notify_text, reply_markup=write_btn(user.user_id),
                                   parse_mode="HTML")
    await message.bot.edit_message_text(text,
                                        reply_markup=next_btn('start'), chat_id=message.chat.id,
                                        message_id=data['past_msg_id'], parse_mode="HTML")


@change_status_router.message(ChangeStatus.input_time_to_base)
async def input_time_to_base_handler(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()

    user: Users = Users.get_or_none(Users.user_id == message.from_user.id)
    user.status = 0
    user.points = 0
    user.points_done = 0
    user.save()
    await state.clear()
    text = f'Водитель <i>{user.fullname}</i> с номером ТС <i>{user.number_car}</i> будет на РЦ через <i>{message.text}</i>'

    await message.bot.send_message(os.getenv('CHANNEL_ID'), text, reply_markup=write_btn(user.user_id),
                                   parse_mode="HTML")
    await message.bot.edit_message_text(
        f'✅ Вы сменили свой статус на <i>«В пути на РЦ»</i>, будете через <i>{message.text} минут</i>',
        reply_markup=next_btn('start'), chat_id=message.chat.id, message_id=data['past_msg_id'], parse_mode="HTML")
