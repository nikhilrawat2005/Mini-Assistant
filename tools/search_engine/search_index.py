import sqlite3
from datetime import datetime

def init_db(db_path='search_db.sqlite'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            category TEXT NOT NULL,
            snippet TEXT NOT NULL,
            keywords TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def store_result(db_path, url, category, snippet, keywords):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO results (url, category, snippet, keywords, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (url, category, snippet, keywords, datetime.now()))
        conn.commit()
    except Exception as e:
        print(f"Database error: {str(e)}")
    finally:
        conn.close()