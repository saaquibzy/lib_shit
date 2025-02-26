import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
import uuid  # For generating unique reset tokens

# ✅ Create a connection to the remote MySQL database
def create_connection():
    host = "192.168.29.55"  # Remote server IP
    user = "remote_user"  # Remote MySQL username
    password = "securepassword"  # Remote MySQL password
    database = "library_db"  # Database name

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            print("✅ Connected to MySQL Server")
            return connection  # Return the connection object
        else:
            print("❌ Failed to connect to MySQL server")
            return None

    except Error as e:
        print(f"⚠️ Connection Error: {e}")
        return None


# ==============================
# ✅ USER MANAGEMENT FUNCTIONS
# ==============================

# Function to register a new user
def register_user(username, email, password, role="user"):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Check if username or email already exists
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                print("❌ Username or Email already exists! Please choose a different one.")
                return False  # Prevent duplicate accounts

            # Hash the password before storing it
            hashed_password = generate_password_hash(password)

            # Insert user into database
            insert_query = "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (username, email, hashed_password, role))
            connection.commit()
            print("✅ User registered successfully!")
            return True  # Registration successful

        except Error as e:
            print(f"⚠️ Error registering user: {e}")
            return False  # Registration failed

        finally:
            cursor.close()
            connection.close()


# Function to authenticate user login
def authenticate_user(username, password):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            select_query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(select_query, (username,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            # Check password hash
            if user and check_password_hash(user["password"], password):
                return user  # Return user details if login is successful
            else:
                return None  # Invalid credentials

        except Error as e:
            print(f"⚠️ Error authenticating user: {e}")
            return None


# Function to check if a user is an admin
def is_admin(user_id):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            select_query = "SELECT role FROM users WHERE id = %s"
            cursor.execute(select_query, (user_id,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            return user and user["role"] == "admin"
        except Error as e:
            print(f"⚠️ Error checking admin status: {e}")
            return False


# ==============================
# ✅ BOOK MANAGEMENT FUNCTIONS
# ==============================

# Function to add a new book
def add_book(book_id, title, author, year, genre, copies):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO books (id, title, author, year_published, genre, available_copies)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (book_id, title, author, year, genre, copies))
            connection.commit()
            print("✅ Book added successfully!")
        except Error as e:
            print(f"⚠️ Error adding book: {e}")
        finally:
            connection.close()


# Function to get all books
def get_books():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM books")
            books = cursor.fetchall()
            connection.close()
            return books
        except Error as e:
            print(f"⚠️ Error fetching books: {e}")
            return []


# Function to delete a book
def delete_book(book_id):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
            connection.commit()
            print(f"✅ Book {book_id} deleted successfully!")
        except Error as e:
            print(f"⚠️ Error deleting book: {e}")
        finally:
            connection.close()


# ==============================
# ✅ NEW FEATURES: RESERVATION & REVIEWS
# ==============================

# Function to reserve a book
def reserve_book(book_id, user_id):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO reservations (user_id, book_id) VALUES (%s, %s)", (user_id, book_id))
            connection.commit()
            print(f"✅ Book {book_id} reserved successfully!")
        except Error as e:
            print(f"⚠️ Error reserving book: {e}")
        finally:
            connection.close()


# Function to add a book review
def add_review(user_id, book_id, review_text, rating):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO reviews (user_id, book_id, review_text, rating)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (user_id, book_id, review_text, rating))
            connection.commit()
            print("✅ Review added successfully!")
        except Error as e:
            print(f"⚠️ Error adding review: {e}")
        finally:
            connection.close()


# ==============================
# ✅ FORGOT PASSWORD FUNCTION
# ==============================

# Function to request a password reset
def request_password_reset(email):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            reset_token = str(uuid.uuid4())  # Generate a unique token
            cursor.execute("UPDATE users SET reset_token = %s WHERE email = %s", (reset_token, email))
            connection.commit()
            print(f"🔑 Password reset requested. Token: {reset_token}")
            return reset_token
        except Error as e:
            print(f"⚠️ Error requesting password reset: {e}")
            return None
        finally:
            connection.close()
