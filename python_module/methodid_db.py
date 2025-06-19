import sqlite3

def update_methodid_db(method_id, function):
    conn = sqlite3.connect('methodids.db')
    conn.execute("INSERT INTO methodids VALUES (?, ?)", (method_id, function))
    conn.commit()
