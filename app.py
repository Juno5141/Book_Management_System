from flask import Flask, render_template, request, redirect, url_for, flash, Response
import sqlite3
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for flashing messages


def get_db_connection():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn

if not os.path.exists('books.db'):
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            release_date TEXT,
            genre TEXT,
            status TEXT,
            notes TEXT
        );
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():

    query = request.form.get('query', '') if request.method == 'POST' else ''
    sort = request.args.get('sort', 'title')
    order = request.args.get('order', 'asc')

    sort_columns = ['title', 'author', 'release_date', 'genre', 'status']
    if sort not in sort_columns:
        sort = 'title'
    if order not in ['asc', 'desc']:
        order = 'asc'

    conn = get_db_connection()
    if query:
        books = conn.execute(f'''SELECT * FROM books WHERE
                                  title LIKE ? OR
                                  author LIKE ? OR
                                  genre LIKE ? OR
                                  status LIKE ?
                                  ORDER BY {sort} {order}''',
                              [f'%{query}%']*4).fetchall()
    else:
        books = conn.execute(f'SELECT * FROM books ORDER BY {sort} {order}').fetchall()

    status_counts = conn.execute('''
        SELECT status, COUNT(*) as count FROM books GROUP BY status
    ''').fetchall()

    conn.close()
    return render_template('index.html', books=books, query=query, sort=sort, order=order, status_counts=status_counts)

@app.route('/export')
def export_books():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Title', 'Author', 'Release Date', 'Genre', 'Status', 'Notes'])
    for book in books:
        writer.writerow([book['id'], book['title'], book['author'], book['release_date'], book['genre'], book['status'], book['notes']])

    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=bookList.csv'
    return response

@app.route('/add', methods=['POST'])
def add_book():
    title = request.form['title'].strip()
    author = request.form['author'].strip()
    release_date = request.form['release_date']
    genre = request.form['genre']
    status = request.form['status']
    notes = request.form['notes']

    conn = get_db_connection()
    existing = conn.execute('SELECT * FROM books WHERE LOWER(title) = ? AND LOWER(author) = ?',
                            (title.lower(), author.lower())).fetchone()
    if existing:
        flash('⚠️ This book already exists in your collection (same title and author).', 'warning')
    else:
        conn.execute('INSERT INTO books (title, author, release_date, genre, status, notes) VALUES (?, ?, ?, ?, ?, ?)',
                     (title, author, release_date, genre, status, notes))
        conn.commit()
        flash('✅ Book added successfully!', 'success')

    conn.close()
    return redirect(url_for('index'))


@app.route('/edit/<int:book_id>')
def edit_form(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    conn.close()
    return render_template('edit.html', book=book)


@app.route('/update/<int:book_id>', methods=['POST'])
def update_book(book_id):
    title = request.form['title']
    author = request.form['author']
    release_date = request.form['release_date']
    genre = request.form['genre']
    status = request.form['status']
    notes = request.form['notes']

    conn = get_db_connection()
    conn.execute('''UPDATE books SET title = ?, author = ?, release_date = ?, genre = ?, status = ?, notes = ?
                    WHERE id = ?''',
                 (title, author, release_date, genre, status, notes, book_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/recommend/<int:book_id>')
def recommend(book_id):
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    selected_book = None
    texts = []

    for book in books:
        combined = f"{book['author']} {book['genre']} {book['status']}"
        texts.append(combined)
        if book['id'] == book_id:
            selected_book = book

    if not selected_book:
        return redirect(url_for('index'))

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    similarities = cosine_similarity(tfidf_matrix)

    selected_index = [i for i, b in enumerate(books) if b['id'] == book_id][0]
    scores = list(enumerate(similarities[selected_index]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    recommended_books = [books[i] for i, score in scores[1:6]]  # top 5 excluding self
    conn.close()

    return render_template('recommend.html', book=selected_book, recommendations=recommended_books)


@app.route('/delete/<int:book_id>')
def delete_book(book_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
