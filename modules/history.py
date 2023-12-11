import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart

from modules.registration import RegistrationDp

from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from database.db import RideDB


dp_hsitory = Router()
db = RideDB()
db.create_tables()


@dp_hsitory.message(Command('history'))
async def command_history_handler(message: Message) -> None:
    history = db.get_passenger_history(message.from_user.id)
    ride = db.get_ride(history[-1]['ride_id'])
    other_role = 'driver' if db.get_user(message.from_user.id)['role'] == 'passenger' else 'passenger'
    other_role_name = db.get_user(ride[other_role])['name']


    if not history:
        await message.answer('You have no history.')
        return
    
    text = 'Your ride history:\n\n'
    for his in history:
        ride = db.get_ride(his['ride_id'])
        text += f'From: {ride["location"]}\n'
        text += f'To: {ride["destination"]}\n'
        text += f'{other_role}: {other_role_name}\n'
        text += '\n'

    await message.answer(text, reply_markup=ReplyKeyboardRemove())
    return

def generate_ride_receipt(ride, user_role, other_role, other_role_name):
    text = 'Your ride receipt:\n\n'
    text += f'Ride ID: {ride["ride_id"]}\n'
    text += f'From: {ride["location"]}\n'
    text += f'To: {ride["destination"]}\n'
    text += f'{other_role}: {other_role_name}\n'
    text += f'Fare: {ride["fare"]}\n'
    text += '\n'
    return text

@dp_hsitory.message(Command('receipt'))
async def command_receipt_handler(message: Message) -> None:
    history = db.get_passenger_history(message.from_user.id)
    ride = db.get_ride(history[-1]['ride_id'])

    if ride['status'] != 'completed':
        await message.answer('You ride has not been completed yet.')
        return
    
    other_role = 'driver' if db.get_user(message.from_user.id)['role'] == 'passenger' else 'passenger'
    other_role_name = db.get_user(ride[other_role])['name']

    if not history:
        await message.answer('You have no history.')
        return
    
    text = generate_ride_receipt(ride, db.get_user(message.from_user.id)['role'], other_role, other_role_name)

    await message.answer(text, reply_markup=ReplyKeyboardRemove())
    return


