import asyncio
import logging
import sys
from os import getenv
from typing import Any, Dict

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from database.db import RideDB

db = RideDB()
db.create_tables()

#
registration_dp = Router()

class RegistrationDp(StatesGroup):
    name = State()
    phone = State()
    role = State()



@registration_dp.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationDp.name)
    await message.answer(
        "Welcome to RidePal, please enter your full name?",
        reply_markup=ReplyKeyboardRemove()
    )


@registration_dp.message(Command('cancel'))
@registration_dp.message(F.text.caseFold() == 'cancel')
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = state.get_state()

    if current_state is None:
        return
    
    logging.info('canceling state %r', current_state)
    await state.clear()
    await message.answer('Cancelled.', reply_markup=ReplyKeyboardRemove())


async def show_summary(message: Message, data: Dict[str, Any]) -> None:
    name = data['name']
    phone = data['phone']
    role = data['role']

    text = f'name: {name}\nphone: {phone}\n role: {role}'

    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())


@registration_dp.message(RegistrationDp.name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(RegistrationDp.phone)

    name = message.text

    text = f'''Nice to meet you {name}! Now, please share your phone number using the button below:'''

    # Create a keyboard with a "Share Phone Number" button
    reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Share Phone Number', request_contact=True),
                ],
            ],
            resize_keyboard=True,
        )

    await message.answer(
        text,
        reply_markup=reply_markup
    )


@registration_dp.message(RegistrationDp.phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(RegistrationDp.role)

    phone_number = message.contact.phone_number

    text = f'''Great! Your phone number ({phone_number}) has been received.

Please enter your role using the buttons below:'''

    reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Driver'),
                    KeyboardButton(text='Passenger')
                ],
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

    await message.answer(
        text,
        reply_markup=reply_markup
    )


@registration_dp.message(RegistrationDp.role)
async def process_role(message: Message, state: FSMContext) -> None:
    role = message.text.lower()

    if role in ["driver", "passenger"]:
        await state.update_data(role=role)

        # Retrieve individual values directly from the state
        name = (await state.get_data()).get('name', '')
        phone = (await state.get_data()).get('phone', '')

        # Save user data to the SQLite database
        user_id = message.from_user.id

        db.add_user(user_id, name, phone, role)
            # You can now save the user data to a database or perform further actions
        await message.reply(f"Registration successful!\n\nFull Name: {name}\n"
                            f"Phone Number: {phone}\nRole: {role}",
                            parse_mode=ParseMode.MARKDOWN)

    # await show_summary(message, await state.get_data())

    await state.set_state()