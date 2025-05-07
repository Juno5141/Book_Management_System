import sqlite3

conn = sqlite3.connect('books.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM books")
conn.commit()
conn.close()

print("All books deleted.")
