from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from utils.keyboards import back_btn
from utils.states import Registration
from utils.models import Users

registration_router = Router()


@registration_router.callback_query(F.data == 'registration')
async def registration_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('🪪 Введите свою Имя Фамилию', reply_markup=back_btn('start'))
    await state.set_state(Registration.input_name)
    await state.update_data(past_msg_id=callback.message.message_id)


@registration_router.message(Registration.input_name)
async def input_name_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()

    await state.update_data(name=message.text)
    await message.bot.edit_message_text(f'✅ Вы ввели <i>{message.text}</i>\n'
                                        f'🆔 Теперь введите номер транспорта:', reply_markup=back_btn('registration'),
                                        parse_mode="HTML", chat_id=message.chat.id, message_id=data['past_msg_id'])
    await state.set_state(Registration.input_number)


@registration_router.message(Registration.input_number)
async def input_carid_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()

    username = message.from_user.username if message.from_user.username else 'None'
    user = Users.get_or_none(Users.user_id == message.from_user.id)
    if user:
        user.delete_instance()
    Users.create(user_id=message.from_user.id, username=username, fullname=data['name'], number_car=message.text)

    await state.clear()
    await message.bot.edit_message_text(f'✅ Вы ввели <i>{message.text}</i>\n\n'
                                        f'✨ Теперь вы зарегистрированы в нашем боте, перейдите в главное меню',
                                        reply_markup=back_btn('start'),
                                        parse_mode="HTML", chat_id=message.chat.id, message_id=data['past_msg_id'])
