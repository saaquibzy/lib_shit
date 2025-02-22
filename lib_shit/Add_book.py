import mysql.connector
from test_connection import create_connection
import hashlib  # For password hashin

# Function to hash passwords (for security)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to authenticate the user
def authenticate_user():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Prompt for username and password
            username = input("Enter username: ")
            password = input("Enter password: ")

            # Hash the entered password
            hashed_password = hash_password(password)

            # Query to check if the user exists with the hashed password
            select_query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(select_query, (username, hashed_password))

            user = cursor.fetchone()
            if user:
                print("Login successful!")
                return True  # User authenticated
            else:
                print("Invalid username or password.")
                return False  # Invalid credentials

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

    return False  # Return false if no connection was made


# Add Book Function with Book ID (primary key but not auto-incremented)
def add_book_to_db(book_id, title, author, year_published, genre, available_copies):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # Insert new book with provided book_id
            insert_query = """
            INSERT INTO books (id, title, author, year_published, genre, available_copies)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            book_data = (book_id, title, author, year_published, genre, available_copies)
            cursor.execute(insert_query, book_data)
            connection.commit()
            print("Book added successfully!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

# View Books Function
def view_books():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            select_query = "SELECT * FROM books"
            cursor.execute(select_query)

            books = cursor.fetchall()
            if books:
                print("\nBooks in the Library:")
                for book in books:
                    print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Year Published: {book[3]}, Genre: {book[4]}, Available Copies: {book[5]}")
            else:
                print("No books found.")
        except Exception as e:
            print(f"Error: {e}")

# Update Book Function
def update_book():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Get the book ID and details to update
            book_id = int(input("Enter the book ID to update: "))
            title = input("Enter new title (leave empty to keep current): ")
            author = input("Enter new author (leave empty to keep current): ")
            genre = input("Enter new genre (leave empty to keep current): ")
            year_published = input("Enter new year published (leave empty to keep current): ")
            available_copies = input("Enter new available copies (leave empty to keep current): ")

            # Update the fields with new values
            update_query = "UPDATE books SET title = %s, author = %s, genre = %s, year_published = %s, available_copies = %s WHERE id = %s"
            cursor.execute(update_query, (title or None, author or None, genre or None, year_published or None, available_copies or None, book_id))

            connection.commit()
            if cursor.rowcount > 0:
                print(f"Book with ID {book_id} updated successfully.")
            else:
                print(f"No book found with ID {book_id}.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

# Delete Book Function
def delete_book():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            book_id = int(input("Enter the book ID to delete: "))
            delete_query = "DELETE FROM books WHERE id = %s"
            cursor.execute(delete_query, (book_id,))

            connection.commit()
            if cursor.rowcount > 0:
                print(f"Book with ID {book_id} deleted successfully.")
            else:
                print(f"No book found with ID {book_id}.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

# Search Books Function
def search_books():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            print("\nSearch by:")
            print("1. Title")
            print("2. Author")
            print("3. Genre")
            search_choice = input("Enter your choice (1/2/3): ")

            search_query = ""
            search_value = ""

            if search_choice == '1':  # Search by title
                search_value = input("Enter the title to search: ")
                search_query = "SELECT * FROM books WHERE title LIKE %s"
            elif search_choice == '2':  # Search by author
                search_value = input("Enter the author to search: ")
                search_query = "SELECT * FROM books WHERE author LIKE %s"
            elif search_choice == '3':  # Search by genre
                search_value = input("Enter the genre to search: ")
                search_query = "SELECT * FROM books WHERE genre LIKE %s"
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
                return

            # Execute the search query
            cursor.execute(search_query, ('%' + search_value + '%',))

            books = cursor.fetchall()
            if books:
                print("\nSearch Results:")
                for book in books:
                    print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Year Published: {book[3]}, Genre: {book[4]}, Available Copies: {book[5]}")
            else:
                print("No books found matching your search criteria.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

# Sort Books Function
def sort_books():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Ask the user for sorting criteria
            sort_criteria = input("Sort by:\n1. Year of Publication\n2. Available Copies\nEnter choice (1/2): ")

            if sort_criteria == '1':
                sort_query = "SELECT * FROM books ORDER BY year_published"
            elif sort_criteria == '2':
                sort_query = "SELECT * FROM books ORDER BY available_copies"
            else:
                print("Invalid option.")
                return

            cursor.execute(sort_query)

            books = cursor.fetchall()
            if books:
                print("\nSorted Books:")
                for book in books:
                    print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Year Published: {book[3]}, Genre: {book[4]}, Available Copies: {book[5]}")
            else:
                print("No books found.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

# Main Menu with Authentication Check
if __name__ == "__main__":
    if authenticate_user():  # Check if the user is authenticated before proceeding
        while True:
            print("\n1. Add Book")
            print("2. View All Books")
            print("3. Update Book")
            print("4. Delete Book")
            print("5. Search Books")
            print("6. Sort Books")
            print("7. Exit")
            
            choice = input("Enter your choice: ")

            if choice == '1':
                book_id = int(input("Enter the book ID: "))  # Ask for Book ID
                title = input("Enter the title: ")
                author = input("Enter the author: ")
                year_published = int(input("Enter the year of publication: "))
                genre = input("Enter the genre: ")
                available_copies = int(input("Enter the number of available copies: "))
                add_book_to_db(book_id, title, author, year_published, genre, available_copies)
            elif choice == '2':
                view_books()
            elif choice == '3':
                update_book()
            elif choice == '4':
                delete_book()
            elif choice == '5':
                search_books()
            elif choice == '6':
                sort_books()
            elif choice == '7':
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, or 7.")
    else:
        print("Access denied. Invalid credentials.")