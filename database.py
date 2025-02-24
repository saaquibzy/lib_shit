# test_connection.py
import mysql.connector
from mysql.connector import Error

def create_connection():
    host = "192.168.29.55"
    user = "remote_user"
    password = "securepassword"
    database = "library_db"

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            return connection  # return only the connection object
        else:
            print("Failed to connect to MySQL server")
            return None

    except Error as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    connection = create_connection()
    if connection:
        connection.close()
