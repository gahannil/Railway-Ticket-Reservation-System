import mysql.connector
from getpass import getpass
import hashlib
import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MySQL connection parameters
username = 'root'
password = getpass("Enter your password: ")
host = 'localhost'
database = 'railway_reservation'

try:
    # Establish a connection to the MySQL database
    cnx = mysql.connector.connect(
        user=username,
        password=password,
        host=host,
        database=database
    )
    # Create a cursor object to execute SQL queries
    cursor = cnx.cursor()
    logging.info("Connected to the database successfully.")

except mysql.connector.Error as err:
    logging.error(f"Error connecting to the database: {err}")
    exit(1)


# Function to hash passwords using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Function to validate email using regular expressions
def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


# Function to validate date input
def validate_date(date_str):
    return bool(re.match(r'\d{4}-\d{2}-\d{2}', date_str))


# Function to create tables in the database
def create_tables():
    try:
        # Create tables if they don't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE,
                password VARCHAR(100),
                email VARCHAR(100),
                PRIMARY KEY (id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trains (
                id INT AUTO_INCREMENT,
                train_number INT UNIQUE,
                train_name VARCHAR(100),
                source_station VARCHAR(50),
                destination_station VARCHAR(50),
                fare INT,
                schedule TIME,
                available_seats INT,
                PRIMARY KEY (id)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT,
                user_id INT,
                train_id INT,
                booking_date DATE,
                PRIMARY KEY (id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (train_id) REFERENCES trains(id)
            );
        """)
        cnx.commit()
        logging.info("Tables created successfully.")
    except mysql.connector.Error as err:
        logging.error(f"Error creating tables: {err}")
        cnx.rollback()


# Function to insert sample trains into the database
def insert_sample_trains():
    try:
        sample_trains = [
            (12345, 'Howrah Express', 'Howrah', 'Digha', 150, '08:00:00', 100),
            (67890, 'Darjeeling Mail', 'Sealdah', 'Darjeeling', 500, '22:05:00', 150),
            (11223, 'Kolkata Local', 'Ballygunge', 'Sealdah', 20, '06:30:00', 50),
            (44556, 'Shatabdi Express', 'Howrah', 'New Jalpaiguri', 700, '05:40:00', 200)
        ]
        cursor.executemany("""
            INSERT INTO trains (train_number, train_name, source_station, destination_station, fare, schedule, available_seats)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, sample_trains)
        cnx.commit()
        logging.info("Sample trains inserted successfully.")
    except mysql.connector.Error as err:
        logging.error(f"Error inserting sample trains: {err}")
        cnx.rollback()


# Function to login for users
def login_user(username, password):
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hash_password(password)))
        user = cursor.fetchone()
        return user
    except mysql.connector.Error as err:
        logging.error(f"Error during user login: {err}")
        return None


# Function to signup for users
def signup_user(username, password, email):
    if not validate_email(email):
        print("Invalid email format.")
        return
    try:
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", 
                       (username, hash_password(password), email))
        cnx.commit()
        logging.info("User  signup successful.")
        print("Signup successful! You can now log in.")
    except mysql.connector.Error as err:
        logging.error(f"Error during user signup: {err}")
        print("Signup failed. Username may already exist.")
        cnx.rollback()


# Function to view train schedule
def view_train_schedule():
    try:
        cursor.execute("SELECT * FROM trains")
        trains = cursor.fetchall()

        if not trains:
            print("No trains found.")
            return

        print("Available Trains:")
        for train in trains:
            # Ensure that the number of columns matches what you expect
            train_id = train[0]
            train_number = train[1]
            train_name = train[2]
            source_station = train[3]
            destination_station = train[4]
            schedule = train[5]
            fare = train[6]
            available_seats = train[7] if len(train) > 7 else "N/A"  # Check if available_seats exists

            print(f"Train ID: {train_id}, Train Number: {train_number}, Train Name: {train_name}, "
                  f"Source: {source_station}, Destination: {destination_station}, Schedule: {schedule}, "
                  f"Fare: Rs. {fare}, Available Seats: {available_seats}")
    except mysql.connector.Error as err:
        logging.error(f"Error viewing train schedule: {err}")


# Function to check if a train ID exists
def train_id_exists(train_id):
    try:
        cursor.execute("SELECT id FROM trains WHERE id = %s", (train_id,))
        return cursor.fetchone() is not None
    except mysql.connector.Error as err:
        logging.error(f"Error checking train ID: {err}")
        return False


# Function to calculate total fare
def calculate_total_fare(num_tickets, fare_per_ticket):
    return fare_per_ticket * num_tickets


# Function to book multiple tickets
def book_tickets(user_id, train_id):
    if not train_id_exists(train_id):
        print("Invalid train ID. Please choose a valid train ID.")
        return

    fare_per_ticket = 150  # Example fare per ticket
    max_tickets = 5
    ticket_details = []

    print(f"Enter details for up to {max_tickets} tickets:")
    
    for i in range(max_tickets):
        print(f"\nTicket {i + 1}:")
        name = input("Enter passenger name: ")
        age = input("Enter age of passenger: ")
        gender = input("Enter gender (M/F): ")
        
        ticket_details.append({
            'name': name,
            'age': age,
            'gender': gender
        })

        if i < max_tickets - 1:
            more = input("Do you want to add another ticket? (yes/no): ")
            if more.lower() != 'yes':
                break

    total_fare = calculate_total_fare(len(ticket_details), fare_per_ticket)
    print(f"\nTotal fare for {len(ticket_details)} tickets: Rs. {total_fare}")

    payment_method = input("Enter payment method (e.g., Credit Card, Debit Card): ")
    print(f"Processing payment of Rs. {total_fare} using {payment_method}...")

    # Simulate payment processing
    payment_successful = True  # Simulate payment success (you can add real payment processing logic here)

    if payment_successful:
        # Ask for booking date
        booking_date = input("Enter booking date (YYYY-MM-DD): ")
        if not validate_date(booking_date):
            print("Invalid date format. Please use YYYY-MM-DD.")
            return

        # Insert each booking into the database
        for ticket in ticket_details:
            try:
                cursor.execute("INSERT INTO bookings (user_id, train_id, booking_date) VALUES (%s, %s, %s)", 
                               (user_id, train_id, booking_date))
                cnx.commit()
                logging.info("Ticket booked successfully in the database.")
            except mysql.connector.Error as err:
                logging.error(f"Error booking tickets: {err}")
                cnx.rollback()
                print("Failed to book one or more tickets. Please try again.")
                return

        print("All tickets have been booked successfully.")
        print("Booking Details:")
        for ticket in ticket_details:
            print(ticket)
    else:
        print("Payment failed. Please try again.")


# Function to book a ticket
def book_ticket(user_id, train_id, booking_date):
    if not train_id_exists(train_id):
        print("Invalid train ID. Please choose a valid train ID.")
        return
    if not validate_date(booking_date):
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    # Get fare per ticket (you might want to fetch this from the database)
    fare_per_ticket = 150  # Example fare per ticket

    # Ask for payment method
    payment_method = input("Enter payment method (e.g., Credit Card, Debit Card): ")
    print(f"Processing payment of Rs. {fare_per_ticket} using {payment_method}...")

    # Simulate payment processing
    payment_successful = True  # Simulate payment success (you can add real payment processing logic here)

    if payment_successful:
        try:
            cursor.execute("INSERT INTO bookings (user_id, train_id, booking_date) VALUES (%s, %s, %s)", 
                           (user_id, train_id, booking_date))
            cnx.commit()
            logging.info("Ticket booked successfully.")
            print("Your ticket has been booked.")
        except mysql.connector.Error as err:
            logging.error(f"Error booking ticket: {err}")
            cnx.rollback()
    else:
        print("Payment failed. Please try again.")

# Function to view booked tickets
def view_booked_tickets(user_id):
    try:
        cursor.execute("""
            SELECT b.id, t.train_name, t.source_station, t.destination_station, b.booking_date
            FROM bookings b
            JOIN trains t ON b.train_id = t.id
            WHERE b.user_id = %s
        """, (user_id,))
        tickets = cursor.fetchall()

        if not tickets:
            print("No tickets found.")
            return

        print("\nYour Booked Tickets:")
        for ticket in tickets:
            print(f"Booking ID: {ticket[0]}, Train: {ticket[1]}, Source: {ticket[2]}, Destination: {ticket[3]}, Date: {ticket[4]}")

    except mysql.connector.Error as err:
        logging.error(f"Error viewing booked tickets: {err}")

# Function to cancel a ticket
def cancel_ticket(user_id):
    try:
        booking_id = int(input("Enter Booking ID to cancel: "))
        
        # Check if the booking exists and belongs to the user
        cursor.execute("SELECT id FROM bookings WHERE id = %s AND user_id = %s", (booking_id, user_id))
        booking = cursor.fetchone()

        if not booking:
            print("Invalid Booking ID or you do not own this booking.")
            return

        # Delete the booking
        cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
        cnx.commit()
        logging.info("Ticket canceled successfully.")
        print("Your ticket has been canceled.")
        
    except mysql.connector.Error as err:
        logging.error(f"Error canceling ticket: {err}")
        cnx.rollback()


# Main function to interact with the railway reservation system
def main():
    create_tables()
    insert_sample_trains()

    logged_in_user_id = None  # Variable to store the logged-in user's ID

    while True:
        print("\n=== Railway Reservation System ===")
        print("1. User Login")
        print("2. User Signup")
        print("3. View Train Schedule")
        print("4. Book a Ticket")
        print("5. Book Multiple Tickets")
        print("6. Logout")
        print("7. Exit")
        print("8. View Booked Tickets")
        print("9. Cancel Tickets")

        choice = input("Enter your choice: ")

        if choice == "1":  # User Login
            username = input("Enter username: ")
            password = getpass("Enter password: ")
            user = login_user(username, password)
            if user:
                logged_in_user_id = user[0]  # Store the user's ID
                print(f"Login successful! Welcome, {username}.")
            else:
                print("Invalid username or password.")

        elif choice == "2":  # User Signup
            username = input("Enter username: ")
            password = getpass("Enter password: ")
            email = input("Enter email: ")
            signup_user(username, password, email)

        elif choice == "3":  # View Train Schedule
            view_train_schedule()

        elif choice == "4":  # Book a Ticket
            if logged_in_user_id is None:  # Ensure the user is logged in
                print("You must log in to book tickets.")
                continue
            train_id = int(input("Enter train ID: "))
            booking_date = input("Enter booking date (YYYY-MM-DD): ")
            book_ticket(logged_in_user_id, train_id, booking_date)

        elif choice == "5":  # Book Multiple Tickets
            if logged_in_user_id is None:  # Ensure the user is logged in
                print("You must log in to book tickets.")
                continue
            train_id = int(input("Enter train ID: "))
            book_tickets(logged_in_user_id, train_id)

        elif choice == "6":  # Logout
            if logged_in_user_id is None:  # Check if the user is logged in
                print("You must log in to log out.")
            else:
                logged_in_user_id = None
                print("You have been logged out.")

        elif choice == "7":  # Exit
            print("Exiting the system. Goodbye!")
            break

        elif choice == "8":  # View Booked Tickets
            if logged_in_user_id is None:
                print("You must log in to view your booked tickets.")
                continue
            view_booked_tickets(logged_in_user_id)

        elif choice == "9":  # Cancel Tickets
            if logged_in_user_id is None:
                print("You must log in to cancel tickets.")
                continue
            cancel_ticket(logged_in_user_id)

        else:
            print("Invalid choice. Please try again.")

    # Close the cursor and connection
    cursor.close()
    cnx.close()
    logging.info("Database connection closed.")


if __name__ == "__main__":
    main()