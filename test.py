# Example usage in test.py
from database.db import RideDB

# Create an instance of RideDB
database = RideDB()

# Create tables if they don't exist
database.create_tables()

# Add a user
# database.add_user("user123", "driver", "1234567890")

# Edit the user role
# database.edit_user_attribute("user123", "role", "passenger")

# Remove the user
database.remove_user("385768831")

# Read the user
# user_info = database.get_user_info("userg123")

# if user_info:
#     print("User Information:")
#     print(f"User ID: {user_info['user_id']}")
#     print(f"Role: {user_info['role']}")
#     print(f"Phone: {user_info['phone']}")


# Close the connection when done
database.close_connection()
