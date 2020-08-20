import urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET
import sqlite3
print("heyo")

conn = sqlite3.connect('averaged_scores.sqlite')
cur = conn.cursor()


cur.executescript('''
DROP TABLE IF EXISTS Ratings;

CREATE TABLE "Ratings" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"person_id"	TEXT NOT NULL,
    "cat_name"  TEXT NOT NULL,
    "cat_code"  TEXT NOT NULL,
    "sig_code"  TEXT NOT NULL,
    "rating"    INTEGER NOT NULL,
	"adj_rating"	INTEGER

);

''')

r_a='ratings_all.txt'
ratings_01 = open(r_a)

for line in ratings_01:
	col=line.split('|')
	person_id=col[0]
	cat_name=col[2]
	cat_code=col[3]
	sig_code=col[4]
	rating=col[5]
	print(person_id)

	cur.execute('''INSERT OR IGNORE INTO Ratings (person_id, cat_name, cat_code, sig_code, rating)
		VALUES ( ?,?,?,?,? )''' , ( person_id, cat_name, cat_code , sig_code , rating) )
	cur.execute('SELECT id FROM Ratings WHERE person_id = ? ', ( person_id, ) )
	rating_id=cur.fetchone()[0]
	conn.commit()
