import sqlite3

conn = sqlite3.connect('Too_Easy_Travel.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS history_search(
    user_id INTEGER, command TEXT, date_now DATE , hotels TEXT )
""")
conn.commit()
conn.close()


def sqlite_create(user_id: int, command: str, date_now: str, hotel: str) -> None:
    con = sqlite3.connect('Too_Easy_Travel.db')
    curr = con.cursor()
    curr.execute('INSERT INTO history_search (user_id, command, date_now, hotels) VALUES (?, ?,?, ?);',
                 (user_id, command, date_now, hotel))
    con.commit()
    con.close()
