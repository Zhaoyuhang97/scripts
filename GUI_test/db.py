import sqlite3
from datetime import datetime


def init_db():
    conn = sqlite3.connect('knowledge.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS articles
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
