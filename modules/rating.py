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


dp_rating = Router()
db = RideDB()
db.create_tables()


class RatingStates(StatesGroup):
    rater = State()
    rated = State()
    rating = State()
    feedback = State()


@dp_rating.message(Command('rate'))
async def cmd_rate(message: types.Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    matched_ride = db.get_matched_ride_by_passenger(user['id'])
    rated_role = 'driver' if user['role'] == 'passenger' else 'passenger'
    
    await state.update_data(rater=user['id'])
    await state.update_data(rated=matched_ride['driver'])
    
    await state.set_state(RatingStates.rating)
    
    await message.reply(f"Please rate your {rated_role} from 1 to 5.", reply_markup=ReplyKeyboardRemove())


@dp_rating.message(RatingStates.rating)
async def process_rating(message: types.Message, state: FSMContext):
    rating = message.text
    
    await state.update_data(rating=rating)
    
    await state.set_state(RatingStates.feedback)
    
    await message.reply("Please enter any feedback you have for your driver.", reply_markup=ReplyKeyboardRemove())


@dp_rating.message(RatingStates.feedback)
async def process_feedback(message: types.Message, state: FSMContext):
    feedback = message.text
    
    data = await state.get_data()
    
    rater = data['rater']
    rated = data['rated']
    rating = data['rating']
    
    db.add_rating(rater, rated, rating, feedback)
    
    
    await message.reply("Thank you for your feedback!", reply_markup=ReplyKeyboardRemove())
    
    await state.set_state()


