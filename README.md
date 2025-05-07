#  Book Management System

A simple Book Tracker built with Flask and SQLite.

## Features

- Add books with title, author, release date, genre, status, and notes
- View books in a searchable and sortable table
- Update or delete book entries
- Smart duplicate prevention (by title + author)
- Get recommendations based on genre/author/status using TF-IDF Vectorizer and Cosine similarity
- Dashboard summary with reading status counts
- Export your book collection to CSV
- Clean, responsive UI using Bootstrap 5


## Setup

1. Clone this repo:
   ```bash
   git clone https://github.com/Juno5141/Book_Management_System.git
   cd Book_Management_System

2. Create a venv:
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\\Scripts\\activate

3. Install Dependencies

    pip install flask scikit-learn

4. Run

    python app.py
    Open http://localhost:5000 in your browser.

Notes: SQLite is being usesd to demo; Can upgrade to MySQL server

## For testing purposes

    1. You can run import.py which will import 50 random books into the system
    2. clear_books.py will clear the database
