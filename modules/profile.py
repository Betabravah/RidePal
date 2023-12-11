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


dp_profile = Router()
db = RideDB()
db.create_tables()


class ProfileStates(StatesGroup):
    waiting_for_edit_choice = State()
    waiting_for_new_full_name = State()
    waiting_for_new_phone = State()
    waiting_for_new_role = State()


@dp_profile.message(Command('editprofile'))
async def cmd_edit_profile(message: types.Message, state: FSMContext):
    await state.set_state(ProfileStates.waiting_for_edit_choice)

    reply_markup = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text="Full Name"),
        KeyboardButton(text="Phone Number"),
        KeyboardButton(text="Role"),
    ]],
    resize_keyboard=True, one_time_keyboard=True)
    
    await message.reply("What would you like to edit?",
                        reply_markup=reply_markup)


@dp_profile.message(ProfileStates.waiting_for_edit_choice)
async def process_edit_choice(message: types.Message, state: FSMContext):
    edit_choice = message.text.lower()

    if edit_choice in ["full name", "phone number", "role"]:
        await state.update_data(edit_choice=edit_choice)

        if edit_choice == "full name":
            await message.reply("Please enter your new full name.")
            await state.set_state(ProfileStates.waiting_for_new_full_name)
            
        elif edit_choice == "phone number":
            reply_markup = ReplyKeyboardMarkup(keyboard=[[
                                KeyboardButton(text="Share my phone number", request_contact=True)
                            ]],
              resize_keyboard=True, 
              one_time_keyboard=True
              )
            
            await message.reply("Please share your new phone number using the 'Share my phone number' button.",
                                reply_markup=reply_markup)
            await state.set_state(ProfileStates.waiting_for_new_phone)

        elif edit_choice == "role":
            reply_markup = ReplyKeyboardMarkup(
                keyboard=[[
                        KeyboardButton(text="Driver"),
                        KeyboardButton(text="Passenger"),
            ]],
             resize_keyboard=True, 
             one_time_keyboard=True)

            await message.reply("Please choose your new role:",
                                reply_markup=reply_markup)
            await state.set_state(ProfileStates.waiting_for_new_role)

    else:
        await message.reply("Invalid choice. Please choose 'Full Name', 'Phone Number', or 'Role'.")


@dp_profile.message(ProfileStates.waiting_for_new_full_name)
async def process_new_full_name(message: types.Message, state: FSMContext):
    new_full_name = message.text
    await state.update_data(name=new_full_name)

    await apply_profile_changes(message, state)

    
    user_id = message.from_user.id
    db.update_user(user_id, 'name', new_full_name)


@dp_profile.message(ProfileStates.waiting_for_new_phone)
async def process_new_phone_number(message: types.Message, state: FSMContext):
    new_phone_number = message.contact.phone_number
    await state.update_data(phone=new_phone_number)

    await apply_profile_changes(message, state)

    user_id = message.from_user.id
    db.update_user(user_id, 'phone', new_phone_number)


@dp_profile.message(ProfileStates.waiting_for_new_role)
async def process_new_role(message: types.Message, state: FSMContext):
    new_role = message.text.lower()

    if new_role in ["driver", "passenger"]:
        await state.update_data(role=new_role)

        await apply_profile_changes(message, state)
    else:
        await message.reply("Invalid role. Please choose 'Driver' or 'Passenger'.")


    user_id = message.from_user.id
    db.update_user(user_id, 'role', new_role)


async def apply_profile_changes(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    edit_choice = user_data['edit_choice']

    if edit_choice == 'full name':
        edit_choice = 'name'
    elif edit_choice == 'phone number':
        edit_choice = 'phone'
    elif edit_choice == 'role':
        edit_choice = 'role'
    
    new_value = user_data[edit_choice]

    # Update the user's profile (You should save this data to a database in a real-world application)
    # For now, just print the updated profile information
    await message.reply(f"Profile updated!\n\n{edit_choice}: {new_value}", parse_mode=ParseMode.MARKDOWN)

    # Reset state for the next user
    await state.set_state()



if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp_profile, skip_updates=True)