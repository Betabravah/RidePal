import asyncio
import logging
import sys
import datetime
import random
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
    CallbackQuery,
)

from database.db import RideDB
from constants.bot import bot
from constants.utils import (
    update_ride_status,
    notify_passenger_and_driver
)

db = RideDB()
db.create_tables()

#
ride_dp = Router()

class RideDp(StatesGroup):
    location = State()
    destination = State()
    confirmation = State()
    fare = State()


@ride_dp.message(Command('book'))
async def process_book(message: Message, state: FSMContext) -> None:
    await state.set_state(RideDp.location)

    text = 'Please share your current location'

    await message.answer(
        text,
        reply_markup=ReplyKeyboardRemove()
    )


@ride_dp.message(RideDp.location)
async def process_location(message: Message, state: FSMContext) -> None:
    location = message.text

    await state.update_data(location=location)
    await state.set_state(RideDp.destination)

    text = f'Your current location is {location}. Please enter your destination.'
    
    await message.answer(text, reply_markup=ReplyKeyboardRemove())


@ride_dp.message(RideDp.destination)
async def process_destination(message: Message, state: FSMContext) -> None:
    destination = message.text

    await state.update_data(destination=destination)
    await state.set_state(RideDp.confirmation)

    location = (await state.get_data()).get('location', '')

    fare = random.randint(100, 1000)
    time = random.randint(30, 150)

    await state.update_data(fare=fare)

    text = f'Ride from {location} to {destination}:\n\nFare - {fare} ETB\nEstimated time - {time} minutes.\n\nPlease confirm.'

    keyboards = [
        KeyboardButton(
            text='Cancel',
            callback_data='cancel'
        ),
        KeyboardButton(
            text='Confirm',
        )
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard=[keyboards], resize_keyboard=True
    )

    await message.reply(text, reply_markup=reply_markup)

   

@ride_dp.message(RideDp.confirmation)
async def process_confirmation(message: Message, state: FSMContext) -> None:
    text = message.text.lower()

    if text == 'confirm':
        location = (await state.get_data()).get('location', '')
        destination = (await state.get_data()).get('destination', '')
        
        passenger_id = message.from_user.id
        ride_id = str(passenger_id) + str(datetime.datetime.now())
        fare = (await state.get_data()).get('fare', '')

        db.add_ride(ride_id, passenger_id, location, destination, fare)


        passenger = db.get_user(passenger_id)
        name = passenger['name']
        phone = passenger['phone']

        text = f'Ride from {location} to {destination} has been booked. We will notify you when a driver is available.'
        await message.answer(text, reply_markup=ReplyKeyboardRemove())

        drivers = db.get_drivers()

        for driver in drivers:
            driver_id = driver['user_id']
            print(driver_id)

            text = f'New ride request:\n\nFrom: {location}\nTo: {destination}\nPassenger: {name}\nPhone: {phone}'

            reply_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text='Accept',
                            callback_data=f'accept_{ride_id}'
                        ),
                        InlineKeyboardButton(
                            text='Reject',
                            callback_data=f'reject_{ride_id}'
                        )
                    ]
                ]
            )
            await bot.send_message(driver_id, text, reply_markup=reply_markup)

    
    elif text == 'cancel':
        await message.answer('Ride booking cancelled.', reply_markup=ReplyKeyboardRemove())

    else:
        await message.answer('Please confirm or cancel.', reply_markup=ReplyKeyboardRemove())
    

    
@ride_dp.callback_query(lambda c: c.data.startswith('accept_') or c.data.startswith('reject_'))
async def handle_driver_response(callback_query: CallbackQuery, state: FSMContext):
    data_parts = callback_query.data.split('_')
    action, ride_id = data_parts[0], data_parts[1]

    # Get the driver's decision (accept or reject)
    if action == 'accept':
        # Update ride status to 'accepted'
        update_ride_status(ride_id, 'accepted')

        # Get passenger and driver details
        ride_info = db.get_ride(ride_id)
        passenger_id = ride_info['passenger']
        driver_id = callback_query.from_user.id

        db.add_matched_ride(ride_id, passenger_id, driver_id)
        db.add_history(ride_id, passenger_id, driver_id)

        # Notify the passenger and the driver
        await notify_passenger_and_driver(passenger_id, driver_id, ride_id)
    else:
        # Handle rejection (if needed)
        await bot.send_message(callback_query.from_user.id, "You have rejected the ride request.")
        await state.set_state()

    # Send an acknowledgment message
    await bot.answer_callback_query(callback_query.id, text="You have responded to the ride request.")
    await state.set_state()


@ride_dp.message(Command('completeride'))
async def process_completeride(message: Message, state: FSMContext) -> None:
    await state.set_state(RideDp.location)

    matched_ride = db.get_matched_ride_by_passenger(message.from_user.id)

    if not matched_ride:
        await message.answer('You have no ongoing rides.', reply_markup=ReplyKeyboardRemove())
        await state.set_state()
        return
    
    ride = db.get_ride(matched_ride['ride_id'])

    if not ride:
        await message.answer('You have no ongoing rides.', reply_markup=ReplyKeyboardRemove())
        await state.set_state()
        return

    if ride['status'] == 'completed':
        await message.answer('Ride already completed.', reply_markup=ReplyKeyboardRemove())
        await state.set_state()
        return

    db.update_ride_status(ride['ride_id'], 'completed')
    db.remove_matched_ride(matched_ride['ride_id'])

    await bot.send_message(matched_ride['driver'], f'Ride from {ride["location"]} to {ride["destination"]} completed.')

    await message.answer('Ride completed.', reply_markup=ReplyKeyboardRemove())
    await state.set_state()


@ride_dp.message(Command('cancelride'))
async def process_cancelride(message: Message, state: FSMContext) -> None:
    await state.set_state(RideDp.location)

    ride = db.get_ride_by_passenger(message.from_user.id)
    matched_ride = db.get_matched_ride_by_passenger(message.from_user.id)

    db.update_ride_status(ride['ride_id'], 'cancelled')
    db.remove_matched_ride(matched_ride['ride_id'])

    await bot.send_message(matched_ride['driver'], f'Ride from {ride["location"]} to {ride["destination"]} cancelled.')

    await message.answer('Ride cancelled.', reply_markup=ReplyKeyboardRemove())
    await state.set_state()

    