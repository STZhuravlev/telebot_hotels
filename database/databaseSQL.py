import sqlite3


def sqlite_create(user_id, command, date_now, city):
    conn = sqlite3.connect('Too_Easy_Travel.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS history_search(
        user_id INTEGER, command TEXT, date_now DATE , city TEXT )
    """)
    cur.execute('INSERT INTO history_search (user_id, command, date_now, city) VALUES (?, ?,?, ?);',
                (user_id, command, date_now, city))
    conn.commit()
    conn.close()
