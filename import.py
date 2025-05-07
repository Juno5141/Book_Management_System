import sqlite3
import requests
from random import choice
from time import sleep

subjects = [
    "science_fiction", "romance", "thriller", "history", "biography", "fantasy",
    "mystery", "psychology", "philosophy", "self_help", "drama", "adventure"
]
conn = sqlite3.connect('books.db')
cursor = conn.cursor()

inserted = 0
seen_titles = set()

for subject in subjects:
    url = f"https://openlibrary.org/subjects/{subject}.json?limit=10"
    try:
        response = requests.get(url)
        data = response.json()
        for book in data.get('works', []):
            title = book.get('title')
            if title in seen_titles: continue  # Avoid duplicates
            seen_titles.add(title)
            author = book['authors'][0]['name'] if book.get('authors') else "Unknown"
            genre = subject.replace('_', ' ').title()
            release_date = "2000-01-01"  # Default (OpenLibrary rarely gives full date)
            status = choice(['Owned', 'Wishlist', 'Currently Reading', 'Completed'])
            notes = "Imported via OpenLibrary API"

            cursor.execute(
                "INSERT INTO books (title, author, release_date, genre, status, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (title, author, release_date, genre, status, notes)
            )
            inserted += 1
            if inserted >= 50:
                break
        if inserted >= 50:
            break
        sleep(0.5) 
    except Exception as e:
        print(f"Error fetching from {subject}: {e}")

conn.commit()
conn.close()
print(f"Successfully imported {inserted} books from OpenLibrary.")
