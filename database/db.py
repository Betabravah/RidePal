import sqlite3

class RideDB:
    def __init__(self, db_file='ride_bot.sqlite'):
        self.conn = sqlite3.connect(db_file)
        self.history_count = 0


    ###### Create Tables Operations ######

    def create_tables(self):
        cursor = self.conn.cursor()

        create_user_table_query = """
        CREATE TABLE IF NOT EXISTS user (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            phone TEXT,
            role TEXT
        );
        """

        create_ride_table_query = """
        CREATE TABLE IF NOT EXISTS ride (
            ride_id TEXT PRIMARY KEY,
            passenger TEXT,
            location TEXT,
            destination TEXT,
            fare TEXT,
            status TEXT DEFAULT 'pending'
        );
        """

        create_matched_ride_table_query = """
        CREATE TABLE IF NOT EXISTS matchedride (
            ride_id TEXT PRIMARY KEY,
            passenger TEXT,
            driver TEXT
        );
        """

        create_rating_table_query = """
        CREATE TABLE IF NOT EXISTS rating (
            rating_id TEXT PRIMARY KEY,
            rater TEXT,
            rated TEXT,
            feedback TEXT default 'No feedback'
        );
        """

        create_history_table_query = """
        CREATE TABLE IF NOT EXISTS history (
            history_id TEXT PRIMARY KEY,
            ride_id TEXT,
            passenger TEXT,
            driver TEXT
        );
        """

        cursor.execute(create_user_table_query)
        cursor.execute(create_ride_table_query)
        cursor.execute(create_matched_ride_table_query)
        cursor.execute(create_rating_table_query)
        cursor.execute(create_history_table_query)

        self.conn.commit()


    ###### User CRUD Operations ######

    def add_user(self, user_id, name, phone, role):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO user (user_id, name, phone, role) VALUES (?, ?, ?, ?)", (user_id, name, phone, role))
            self.conn.commit()
            print(f"User added: {user_id}")
        except sqlite3.Error as e:
            print(f"Error adding user: {e}")

    def get_user(self, user_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM user WHERE user_id = ?", (user_id,))
            user_info = cursor.fetchone()

            if user_info:
                user_dict = {
                    'user_id': user_info[0],
                    'name': user_info[1],
                    'phone': user_info[2],
                    'role': user_info[3]
                }
                return user_dict
            else:
                print(f"No user found with user_id: {user_id}")
                return None
        except sqlite3.Error as e:
            print(f"Error retrieving user information: {e}")
            return None


    def update_user(self, user_id, attribute_name, new_value):
        cursor = self.conn.cursor()

        if attribute_name not in ['name', 'role', 'phone']:
            print("Invalid attribute name. Use 'role' or 'phone'.")
            return

        try:
            update_query = f"UPDATE user SET {attribute_name} = ? WHERE user_id = ?"
            cursor.execute(update_query, (new_value, user_id))
            self.conn.commit()
            print(f"User {user_id} {attribute_name} updated: {new_value}")
        except sqlite3.Error as e:
            print(f"Error updating user {attribute_name}: {e}")

    def remove_user(self, user_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM user WHERE user_id = ?", (user_id,))
            self.conn.commit()
            print(f"User removed: {user_id}")
        except sqlite3.Error as e:
            print(f"Error removing user: {e}")

    def get_drivers(self):
        cursor = self.conn.cursor()
        fetch_drivers_query = "SELECT * FROM user WHERE role = 'driver'"
        
        try:
            cursor.execute(fetch_drivers_query)
            drivers = cursor.fetchall()

            driver_list = []
            for driver in drivers:
                user_id, name, phone, role = driver
                driver_info = {
                    'user_id': user_id,
                    'name': name,
                    'phone': phone,
                    'role': role
                }
                driver_list.append(driver_info)

            return driver_list

        except sqlite3.Error as e:
            print(f"Error retrieving drivers: {e}")
            return None

    
    ###### Ride CRUD Operations ######

    def add_ride(self, ride_id, passenger, location, destination, fare):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO ride (ride_id, passenger, location, destination, fare) VALUES (?, ?, ?, ?, ?)", (ride_id, passenger, location, destination, fare))
            self.conn.commit()
            print(f"Ride added: {ride_id}")
        except sqlite3.Error as e:
            print(f"Error adding ride: {e}")

    def get_ride(self, ride_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM ride WHERE ride_id = ?", (ride_id,))
            ride_info = cursor.fetchone()

            if ride_info:
                ride_dict = {
                    'ride_id': ride_info[0],
                    'passenger': ride_info[1],
                    'location': ride_info[2],
                    'destination': ride_info[3],
                    'fare': ride_info[4],
                    'status': ride_info[5]
                }
                return ride_dict
            else:
                print(f"No ride found with ride_id: {ride_id}")
                return None
        except sqlite3.Error as e:
            print(f"Error retrieving ride information: {e}")
            return None
        
    def get_ride_by_passenger(self, passenger_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM ride WHERE passenger = ?", (passenger_id,))
            ride_info = cursor.fetchone()


            if ride_info:
                ride_dict = {
                    'ride_id': ride_info[0],
                    'passenger': ride_info[1],
                    'location': ride_info[2],
                    'destination': ride_info[3],
                    'fare': ride_info[4],
                    'status': ride_info[4]
                }
                return ride_dict
            else:
                print(f"No ride found for passenger: {passenger_id}")
                return None
        except sqlite3.Error as e:
            print(f"Error retrieving ride information: {e}")
            return None


    def edit_ride_location(self, ride_id, new_location):
        cursor = self.conn.cursor()
        try:
            cursor.execute("UPDATE ride SET location = ? WHERE ride_id = ?", (new_location, ride_id))
            self.conn.commit()
            print(f"Ride location updated: {ride_id}")
        except sqlite3.Error as e:
            print(f"Error updating ride location: {e}")


    def remove_ride(self, ride_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM ride WHERE ride_id = ?", (ride_id,))
            self.conn.commit()
            print(f"Ride removed: {ride_id}")
        except sqlite3.Error as e:
            print(f"Error removing ride: {e}")

    def get_ride_status(self, ride_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT status FROM ride WHERE ride_id = ?", (ride_id,))
            status = cursor.fetchone()[0]

            if status:
                return status
            else:
                print(f"No ride found with ride_id: {ride_id}")
                return None
        except sqlite3.Error as e:
            print(f"Error retrieving ride status: {e}")
            return None
        
    def update_ride_status(self, ride_id, new_status):
        cursor = self.conn.cursor()
        try:
            cursor.execute("UPDATE ride SET status = ? WHERE ride_id = ?", (new_status, ride_id))
            self.conn.commit()
            print(f"Ride status updated: {ride_id}")
        except sqlite3.Error as e:
            print(f"Error updating ride status: {e}")



    ###### Matched Ride CRUD Operations ######
    def add_matched_ride(self, ride_id, passenger, driver):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO matchedride (ride_id, passenger, driver) VALUES (?, ?, ?)", (ride_id, passenger, driver))
            self.conn.commit()
            print(f"Matched ride added: {ride_id}")
        except sqlite3.Error as e:
            print(f"Error adding matched ride: {e}")

    def get_matched_ride(self, ride_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM matchedride WHERE ride_id = ?", (ride_id,))
            ride_info = cursor.fetchone()

            if ride_info:
                ride_dict = {
                    'ride_id': ride_info[0],
                    'passenger': ride_info[1],
                    'driver': ride_info[2]
                }
                return ride_dict
            else:
                print(f"No matched ride found with ride_id: {ride_id}")
                return None
        except sqlite3.Error as e:
            print(f"Error retrieving matched ride information: {e}")
            return None
        
    def get_matched_ride_by_passenger(self, passenger_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM matchedride WHERE passenger = ?", (passenger_id,))
            ride_info = cursor.fetchone()

            if ride_info:
                ride_dict = {
                    'ride_id': ride_info[0],
                    'passenger': ride_info[1],
                    'driver': ride_info[2]
                }
                return ride_dict
            else:
                print(f"No matched ride found for passenger: {passenger_id}")
                return None
        except sqlite3.Error as e:
            print(f"Error retrieving matched ride information: {e}")
            return None
        
    def get_matched_ride_by_driver(self, driver_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM matchedride WHERE driver = ?", (driver_id,))
            ride_info = cursor.fetchone()

            if ride_info:
                ride_dict = {
                    'ride_id': ride_info[0],
                    'passenger': ride_info[1],
                    'driver': ride_info[2]
                }
                return ride_dict
            else:
                print(f"No matched ride found for driver: {driver_id}")
                return None
        except sqlite3.Error as e:
            print(f"Error retrieving matched ride information: {e}")
            return None
        
    def remove_matched_ride(self, ride_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM matchedride WHERE ride_id = ?", (ride_id,))
            self.conn.commit()
            print(f"Matched ride removed: {ride_id}")
        except sqlite3.Error as e:
            print(f"Error removing matched ride: {e}")



    ###### Rating CRUD Operations ######
    def add_rating(self, rating_id, rater, rated, feedback):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO rating (rating_id, rater, rated, feedback) VALUES (?, ?, ?, ?)", (rating_id, rater, rated, feedback))
            self.conn.commit()
            print(f"Rating added: {rating_id}")
        except sqlite3.Error as e:
            print(f"Error adding rating: {e}")

    def get_rating(self, rating_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM rating WHERE rating_id = ?", (rating_id,))
            rating_info = cursor.fetchone()

            if rating_info:
                rating_dict = {
                    'rating_id': rating_info[0],
                    'rater': rating_info[1],
                    'rated': rating_info[2],
                    'feedback': rating_info[3]
                }
                return rating_dict
            else:
                print(f"No rating found with rating_id: {rating_id}")
                return None
        except sqlite3.Error as e:
            print(f"Error retrieving rating information: {e}")
            return None
        
    def get_rating_by_rater(self, rater_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM rating WHERE rater = ?", (rater_id,))
            rating_info = cursor.fetchone()

            if rating_info:
                rating_dict = {
                    'rating_id': rating_info[0],
                    'rater': rating_info[1],
                    'rated': rating_info[2],
                    'feedback': rating_info[3]
                }
                return rating_dict
            else:
                print(f"No rating found for rater: {rater_id}")
                return None
        except sqlite3.Error as e:
            print(f"Error retrieving rating information: {e}")
            return None
        
    def get_rating_by_rated(self, rated_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM rating WHERE rated = ?", (rated_id,))
            rating_info = cursor.fetchone()

            if rating_info:
                rating_dict = {
                    'rating_id': rating_info[0],
                    'rater': rating_info[1],
                    'rated': rating_info[2],
                    'feedback': rating_info[3]
                }
                return rating_dict
            else:
                print(f"No rating found for rated: {rated_id}")
                return None
        except sqlite3.Error as e:
            print(f"Error retrieving rating information: {e}")
            return None
        
    def remove_rating(self, rating_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM rating WHERE rating_id = ?", (rating_id,))
            self.conn.commit()
            print(f"Rating removed: {rating_id}")
        except sqlite3.Error as e:
            print(f"Error removing rating: {e}")


    ###### History Operations ######
    def add_history(self, ride_id, driver, passenger):
        cursor = self.conn.cursor()
        try:
            history_id = self.generate_history_id()
            cursor.execute("INSERT INTO history (history_id, ride_id, driver, passenger) VALUES (?, ?, ?, ?)", (history_id, ride_id, driver, passenger))
            self.conn.commit()
            print(f"History added: {driver}, {passenger}")
        except sqlite3.Error as e:
            print(f"Error adding history: {e}")

    def get_passenger_history(self, passenger):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM history WHERE passenger = ?", (passenger,))
            history_info = cursor.fetchall()

            if not history_info:
                print(f"No history found for passenger: {passenger}")
                return None

            history = []
            for his in history_info:
                history_dict = {
                    'history_id': his[0],
                    'ride_id': his[1],
                    'driver': his[1],
                    'passenger': his[3]
                }
                
                history.append(history_dict)
                
            return history
            
        except sqlite3.Error as e:
            print(f"Error retrieving history information: {e}")
            return None
        
    def get_all_history(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM history")
            history_info = cursor.fetchall()

            history = []
            for his in history_info:
                history_dict = {
                    'history_id': his[0],
                    'ride_id': his[1],
                    'driver': his[1],
                    'passenger': his[3]
                }
                
                history.append(history_dict)

                return history
            else:
                print(f"No history found")
                return None
        except sqlite3.Error as e:
            print(f"Error retrieving history information: {e}")
            return None
        

    
    def generate_history_id(self):
        try:
            history_id = f"history_{self._history_count + 1}"
            self._history_count += 1
            return history_id
        except Exception as e:
            print(f"Error generating history id: {e}")
            return None


    def close_connection(self):
        self.conn.close()




