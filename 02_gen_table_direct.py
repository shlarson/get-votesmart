import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import sqlite3
import csv

print("go go gadget get 0-1 directions")

conn = sqlite3.connect('averaged_scores.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS Direction;

CREATE TABLE "Direction" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    "cat_code"  TEXT NOT NULL,
    "sig_code"  TEXT NOT NULL,
    "direction"    INTEGER NOT NULL
);

''')

sig_dir='all_sig_directions.txt'
abortion_dir=open(sig_dir)

for line in abortion_dir:
	cols=line.split(',')
	sig_code=cols[1]
	cat_code=cols[2]
	direction=cols[4]
	print(sig_code, direction)

	cur.execute('''INSERT OR IGNORE INTO Direction (cat_code, sig_code, direction)
		VALUES ( ?,?,? )''' , ( cat_code , sig_code , direction) )
	cur.execute('SELECT id FROM Direction WHERE sig_code = ? ', ( sig_code, ) )
	direction_id=cur.fetchone()[0]
	conn.commit()
