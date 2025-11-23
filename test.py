import sqlite3

con = sqlite3.connect('database.db')
cursor = con.cursor()

cursor.execute("SELECT * FROM tasks")
rows = cursor.fetchall()

print(rows)
