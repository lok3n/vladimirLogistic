import datetime
import os
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from utils.models import Users, Races
from utils.keyboards import write_btn, back_btn, next_btn, cancel_or_continue, send_location
from utils.states import ChangeStatus
from handlers.start import start_handler

change_status_router = Router()


@change_status_router.callback_query(F.data == 'change_status')
async def change_status_handler(callback: CallbackQuery, state: FSMContext):
    user: Users = Users.get_or_none(Users.user_id == callback.from_user.id)
    await state.clear()
    notify_msg = None

    if not user.status:
        user.status = 1
        user.points_done = 0
        user.points = 0
        text = f'Водитель <i>{user.fullname}</i> с номером ТС <i>{user.number_car}</i> вышел на смену'
        notify_msg = await callback.bot.send_message(os.getenv('CHANNEL_ID'), text,
                                                     reply_markup=write_btn(user.user_id),
                                                     parse_mode="HTML")
        user.notify_msg_id = notify_msg.message_id
        await callback.message.edit_text(f'✅ Вы сменили свой статус на <i>«В пути на РЦ»</i>',
                                         reply_markup=next_btn('start'), parse_mode="HTML")
    elif user.status == 1:
        await callback.message.delete()
        await callback.message.answer(
            'ℹ️ Отправьте Вашу геолокацию для подтверждения того, что Вы находитесь на РЦ',
            reply_markup=send_location())
        await state.set_state(ChangeStatus.send_location_start)
    elif user.status == 2:
        text = 'ℹ️ Введите количество точек выгрузки'
        await state.set_state(ChangeStatus.input_points)
        await state.update_data(past_msg_id=callback.message.message_id)
        await callback.message.edit_text(text, reply_markup=back_btn('start'))

    if user.status == 3:
        user.status = 4
        user.points_done += 1
        text = (f'Водитель <i>{user.fullname}</i> с номером ТС <i>{user.number_car}</i> выгружается на '
                f'<i>{user.points_done}</i> точке, ещё <i>{user.points - user.points_done}</i> точек')
        notify_msg = await callback.bot.send_message(os.getenv('CHANNEL_ID'), text,
                                                     reply_markup=write_btn(user.user_id),
                                                     parse_mode="HTML")
        await callback.message.edit_text(f'✅ Вы сменили свой статус на <i>«Выгружаюсь»</i>\n📍 Текущая точка: '
                                         f'<i>{user.points_done}</i>, осталось <i>{user.points - user.points_done}</i>'
                                         f' точек',
                                         reply_markup=next_btn('start'), parse_mode="HTML")

    elif user.status == 4:
        if user.points_done >= user.points:
            text = '''✅ Вы завершили рейс!
            
1️⃣ Еду на второй рейс
2️⃣ Завершай смену, если не едешь на РЦ'''
            await callback.message.edit_text(text, reply_markup=cancel_or_continue())
        else:
            user.status = 3
            text = f'Водитель <i>{user.fullname}</i> с номером ТС <i>{user.number_car}</i> продолжает маршрут'
            notify_msg = await callback.bot.send_message(os.getenv('CHANNEL_ID'), text,
                                                         reply_markup=write_btn(user.user_id),
                                                         parse_mode="HTML")
            await callback.message.edit_text(f'✅ Вы сменили свой статус на <i>«В рейсе»</i>, езжайте на следующую'
                                             f' точку', reply_markup=next_btn('start'), parse_mode="HTML")
        race = Races.select().where(Races.user_id == int(callback.from_user.id)).order_by(-Races.id)[0]
        points_time = race.points_time.split(';') if race.points_time != '' else []
        points_time.append(str(datetime.datetime.now()))
        race.points_time = ';'.join(points_time)
        race.save()
    if notify_msg is not None:
        user.notify_msg_id = notify_msg.message_id
    user.save()


@change_status_router.message(ChangeStatus.input_points)
async def input_points_handler(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    if not message.text.isdigit():
        return await message.bot.edit_message_text('❌ Ошибка! Можно ввести только цифры\n'
                                                   'ℹ️ Введите количество точек выгрузки',
                                                   reply_markup=next_btn('start'), chat_id=message.chat.id,
                                                   message_id=data['past_msg_id'], parse_mode="HTML")
    elif int(message.text) > 15:
        return await message.bot.edit_message_text('❌ Ошибка! Можно ввести максимум 15 точек\n'
                                                   'ℹ️ Введите количество точек выгрузки',
                                                   reply_markup=next_btn('start'), chat_id=message.chat.id,
                                                   message_id=data['past_msg_id'], parse_mode="HTML")

    user: Users = Users.get_or_none(Users.user_id == message.from_user.id)
    user.status = 3
    user.points = int(message.text)
    text = (f'✅ Вы сменили свой статус на <i>«В рейсе»</i>\n'
            f'📍 Количество точек выгрузки: <i>{message.text} точек</i>\n\n'
            f'👍 Желаем вам приятной дороги\n'
            f'ℹ️ После завершения рейса, не забудьте сменить свой статус!')

    notify_text = f'Водитель <i>{user.fullname}</i> с номером ТС <i>{user.number_car}</i> загрузился на <i>{message.text}</i> точек'
    await state.clear()

    notify_msg = await message.bot.send_message(os.getenv('CHANNEL_ID'), notify_text,
                                                reply_markup=write_btn(user.user_id),
                                                parse_mode="HTML")
    user.notify_msg_id = notify_msg.message_id
    user.save()
    await message.bot.edit_message_text(text,
                                        reply_markup=next_btn('start'), chat_id=message.chat.id,
                                        message_id=data['past_msg_id'], parse_mode="HTML")
    race = Races.create(user_id=message.from_user.id,
                        datetime_start=datetime.datetime.now(),
                        points=int(message.text),
                        fullname=user.fullname,
                        number_car=user.number_car)


@change_status_router.message(ChangeStatus.input_time_to_base)
async def input_time_to_base_handler(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()

    user: Users = Users.get_or_none(Users.user_id == message.from_user.id)
    user.status = 1
    user.points = 0
    user.points_done = 0
    await state.clear()
    text = f'Водитель <i>{user.fullname}</i> с номером ТС <i>{user.number_car}</i> будет на РЦ через <i>{message.text}</i>'

    notify_msg = await message.bot.send_message(os.getenv('CHANNEL_ID'), text, reply_markup=write_btn(user.user_id),
                                                parse_mode="HTML")
    user.notify_msg_id = notify_msg.message_id
    user.save()
    await message.bot.edit_message_text(
        f'✅ Вы сменили свой статус на <i>«В пути на РЦ»</i>, будете через <i>{message.text} минут</i>',
        reply_markup=next_btn('start'), chat_id=message.chat.id, message_id=data['past_msg_id'], parse_mode="HTML")


@change_status_router.message(ChangeStatus.send_location_start, F.location)
async def handle_location(message: Message, state: FSMContext):
    center = (55.695708, 37.428913)
    check = ((message.location.latitude - center[0]) ** 2 + (message.location.longitude - center[1]) ** 2) < 0.003 ** 2
    if check:
        user: Users = Users.get_or_none(Users.user_id == message.from_user.id)
        user.status = 2
        text = f'Водитель <i>{user.fullname}</i> с номером ТС <i>{user.number_car}</i> ждёт погрузки'
        notify_msg = await message.bot.send_message(os.getenv('CHANNEL_ID'), text,
                                                    reply_markup=write_btn(user.user_id),
                                                    parse_mode="HTML")
        await message.answer('✅ Вы сменили свой статус на <i>«Нахожусь на РЦ»</i>',
                             reply_markup=next_btn('start'), parse_mode="HTML")
        user.notify_msg_id = notify_msg.message_id
        user.save()
    else:
        await state.clear()
        await message.answer('❌ Вы находитесь не на РЦ, смените статус когда приедете на РЦ',
                             reply_markup=next_btn('start'))


@change_status_router.message(F.text, ChangeStatus.send_location_cancel)
async def handle_message(message: Message, state: FSMContext):
    if message.text != 'Назад':
        await message.answer('Ошибка! Отправьте локацию или нажмите назад')
    else:
        await start_handler(message, state)


@change_status_router.callback_query(F.data == 'continue_race')
async def continue_race(callback: CallbackQuery, state: FSMContext):
    text = 'ℹ️ Введите сколько времени показывает по навигатору до РЦ, либо завершите смену'
    await state.set_state(ChangeStatus.input_time_to_base)
    await state.update_data(past_msg_id=callback.message.message_id)
    await callback.message.edit_text(text, reply_markup=back_btn('change_status'))
