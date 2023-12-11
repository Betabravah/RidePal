from constants.bot import bot
from database.db import RideDB

db = RideDB()


def update_ride_status(ride_id, status):
    db.update_ride_status(ride_id, status)



async def notify_passenger_and_driver(passenger_id, driver_id, ride_id):
    passenger_info = db.get_user(passenger_id)
    driver_info = db.get_user(driver_id)

    ride = db.get_ride(ride_id)
    location = ride['location']
    destination = ride['destination']

    # Notify the passenger
    passenger_text = f"Your ride request (from {location} to {destination}) has been accepted. Your driver is {driver_info['name']} ({driver_info['phone']})."
    await bot.send_message(passenger_id, passenger_text)

    # Notify the driver
    driver_text = f"You have accepted a ride request (from {location} to {destination}) from {passenger_info['name']} ({passenger_info['phone']})."
    await bot.send_message(driver_id, driver_text)
