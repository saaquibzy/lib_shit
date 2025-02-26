from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import create_connection, authenticate_user, register_user, is_admin
import hashlib  # For password hashing

app_routes = Blueprint('app_routes', __name__)

# ✅ Hash Passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ✅ Home (Redirect to options)
@app_routes.route('/')
def home():
    return redirect(url_for('app_routes.options'))

# ✅ Register Route
@app_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        register_user(username, email, password)  # Register in database
        flash("✅ Account created! Please log in.", "success")
        return redirect(url_for('app_routes.login'))

    return render_template("register.html")

# ✅ Login Route
@app_routes.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('app_routes.options'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)

        print(f"🔍 DEBUG: Trying to log in with Username: {username}")
        print(f"🔍 DEBUG: Entered Password (Hashed): {hashed_password}")

        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT username, password, role FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            stored_hashed_password = user[1]
            print(f"🔍 DEBUG: Stored Password in DB: {stored_hashed_password}")

            if hashed_password == stored_hashed_password:
                print(f"✅ DEBUG: Login successful for {username}!")
                session['user'] = username
                session['role'] = user[2]  # Assuming role is at index 2
                flash("✅ Login successful!", "success")
                return redirect(url_for('app_routes.options'))
            else:
                print(f"❌ DEBUG: Password mismatch for {username}!")

        else:
            print(f"❌ DEBUG: No user found with username {username}!")

        flash("❌ Invalid username or password.", "danger")

    return render_template("login.html")

# ✅ Logout Route
@app_routes.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    flash("✅ Logged out successfully!", "info")
    return redirect(url_for('app_routes.login'))

# ✅ Profile Page
@app_routes.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('app_routes.login'))

    return render_template("profile.html", username=session['user'], role=session.get('role', 'user'))

# ✅ Options Page
@app_routes.route('/options')
def options():
    if 'user' not in session:
        return redirect(url_for('app_routes.login'))

    return render_template("options.html")

# ✅ View Books
@app_routes.route('/books')
def view_books():
    if 'user' not in session:
        return redirect(url_for('app_routes.login'))

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("books.html", books=books)

# ✅ Search Books
@app_routes.route('/search_books', methods=['GET'])
def search_books():
    if 'user' not in session:
        return redirect(url_for('app_routes.login'))

    query = request.args.get('query', '')

    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT * FROM books 
        WHERE title LIKE %s OR author LIKE %s OR genre LIKE %s
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))
    
    books = cursor.fetchall()
    cursor.close()
    connection.close()

    if not books:
        flash("❌ No books found matching your search.", "warning")

    return render_template("books.html", books=books, search_query=query)

# ✅ Sort Books
@app_routes.route('/sort_books', methods=['GET'])
def sort_books():
    if 'user' not in session:
        return redirect(url_for('app_routes.login'))

    sort_by = request.args.get('sort_by', 'year_published')

    allowed_columns = ["title", "author", "year_published", "available_copies"]
    if sort_by not in allowed_columns:
        flash("⚠️ Invalid sorting option!", "danger")
        return redirect(url_for('app_routes.view_books'))

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM books ORDER BY {sort_by} ASC")
    
    books = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("books.html", books=books, sort_by=sort_by)

# ✅ Add Book (Admin Only)
@app_routes.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'user' not in session:
        return redirect(url_for('app_routes.login'))

    if session.get('role') != 'admin':
        flash("❌ Access denied! Only admins can add books.", "danger")
        return redirect(url_for('app_routes.view_books'))

    if request.method == 'POST':
        try:
            book_id = int(request.form['book_id'])
            title = request.form['title']
            author = request.form['author']
            year_published = int(request.form['year_published'])
            genre = request.form['genre']
            available_copies = int(request.form['available_copies'])

            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO books (id, title, author, year_published, genre, available_copies) VALUES (%s, %s, %s, %s, %s, %s)",
                (book_id, title, author, year_published, genre, available_copies)
            )
            connection.commit()
            cursor.close()
            connection.close()

            flash("✅ Book added successfully!", "success")
            return redirect(url_for('app_routes.view_books'))
        except Exception as e:
            flash(f"⚠️ Error: {e}", "danger")

    return render_template("add_book.html")

# ✅ Update Book (Admin Only)
@app_routes.route('/update_book/<int:book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    if 'user' not in session:
        return redirect(url_for('app_routes.login'))

    if session.get('role') != 'admin':
        flash("❌ Access denied! Only admins can update books.", "danger")
        return redirect(url_for('app_routes.view_books'))

    connection = create_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year_published = request.form['year_published']
        genre = request.form['genre']
        available_copies = request.form['available_copies']

        update_query = """
            UPDATE books 
            SET title=%s, author=%s, year_published=%s, genre=%s, available_copies=%s 
            WHERE id=%s
        """
        cursor.execute(update_query, (title, author, year_published, genre, available_copies, book_id))
        connection.commit()
        flash(f"✅ Book with ID {book_id} updated successfully.", "success")
        return redirect(url_for('app_routes.view_books'))

    else:
        cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        book = cursor.fetchone()

        cursor.close()
        connection.close()

        if book:
            return render_template("update_book.html", book=book)
        else:
            flash("❌ Book not found.", "danger")
            return redirect(url_for('app_routes.view_books'))

# ✅ Delete Book (Admin Only)
@app_routes.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    if 'user' not in session:
        return redirect(url_for('app_routes.login'))
    
    if session.get('role') != 'admin':
        flash("❌ Access denied! Only admins can delete books.", "danger")
        return redirect(url_for('app_routes.view_books'))

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
    connection.commit()
    cursor.close()
    connection.close()

    flash(f"✅ Book with ID {book_id} deleted successfully.", "success")
    return redirect(url_for('app_routes.view_books'))
