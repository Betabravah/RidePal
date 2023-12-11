import asyncio
import logging
import sys

from aiogram import Dispatcher

from flask import Flask, request

from modules.registration import registration_dp
from modules.profile import dp_profile as profile_dp
from modules.ride import ride_dp
from modules.rating import dp_rating as rating_dp
from modules.history import dp_hsitory as history_dp

from constants.bot import bot, TOKEN, URL
from database.db import RideDB



app = Flask(__name__)
async def main():
    db = RideDB()
    db.create_tables()

    dp = Dispatcher(bot=bot)

    dp.include_router(registration_dp)
    dp.include_router(profile_dp)
    dp.include_router(ride_dp)
    dp.include_router(rating_dp)
    dp.include_router(history_dp)

    bot.delete_webhook()
    bot.set_webhook(url=URL)

    @app.route('/', methods=['POST'])
    async def webhook():
        await dp.process_update(await request.json)
        return 'ok'
    
    # await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
