import sqlite3

con = sqlite3.connect("log_uploads.db")
cur = con.cursor()

for row in cur.execute("SELECT * FROM entries"):
    print(row)

con.close()
