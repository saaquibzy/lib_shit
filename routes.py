from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import create_connection

app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def home():
    return render_template("index.html")

@app_routes.route('/books')
def view_books():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("books.html", books=books)

@app_routes.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        book_id = request.form['book_id']
        title = request.form['title']
        author = request.form['author']
        year_published = request.form['year_published']
        genre = request.form['genre']
        available_copies = request.form['available_copies']

        connection = create_connection()
        cursor = connection.cursor()
        query = "INSERT INTO books (id, title, author, year_published, genre, available_copies) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (book_id, title, author, year_published, genre, available_copies))
        connection.commit()
        cursor.close()
        connection.close()

        flash("Book added successfully!", "success")
        return redirect(url_for('app_routes.view_books'))
    
    return render_template("add_book.html")
