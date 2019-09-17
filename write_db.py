import sqlite3
import csv

with open('./members.csv', newline='') as f:
    csv_reader = csv.DictReader(f)
    members = [ (row['名字'], row['性別'])   for row in csv_reader]


#print(members)

with open('create_db.sql') as f:
    create_db_sql = f.read()

db = sqlite3.connect('members.db')

with db:
    db.executescript(create_db_sql)
    
    # write variables into db
    db.executemany('INSERT INTO members (name,gender) VALUES(?,?)',members)

# read from db to test write-in
c = db.execute('SELECT * FROM members LIMIT 3')
for row in c:
    print(row)
    