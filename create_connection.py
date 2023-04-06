import sqlite3

def create_connection():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes (title TEXT PRIMARY KEY, content TEXT)''')
    conn.commit()
    return conn
