import urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET
import sqlite3
import re
print('start:')

conn = sqlite3.connect('averaged_scores.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS Averages;

CREATE TABLE "Averages" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"person_id"	TEXT NOT NULL UNIQUE
);
''')

cur.execute('''SELECT DISTINCT person_id FROM Ratings''')
list_persons = cur.fetchall()
for person in list_persons:
	person = person[0]
	cur.execute('''INSERT OR IGNORE INTO Averages (person_id)
		VALUES ( ? )''', (person,))
	conn.commit()

#create a column for each category
cur.execute('''SELECT DISTINCT cat_name FROM Ratings''')
list_catnames = cur.fetchall()

cat_headers = ""
cat_default = ""

for commas in list_catnames:
	#print(commas)
	edit = str(commas[0:])
	edit = edit.replace(',','')
	label = edit.strip('()')
	cat_headers = cat_headers + edit + ","
	cat_default = cat_default + "-1" + ","

	sql_command = "ALTER TABLE Averages ADD %s" % (label)
	print(sql_command)
	cur.execute(sql_command)
	conn.commit()

### this needs to get person
#### commit it, along with the "defualt" thing
##### line by line is PERSON, then each set of CAT scores
cur.execute('''SELECT DISTINCT person_id FROM Ratings''')
list_persons = cur.fetchall()
for person in list_persons:
	person_id = person[0]
	print(' ')
	print('===== person_id = ',person_id)
	print(' ')

	#insert person_id?

	cur.execute('''SELECT DISTINCT cat_name FROM Ratings WHERE person_id=?''', (person_id,))
	cat_names = cur.fetchall()

	for cat in cat_names:
		cat = str(cat)
		cat = cat.strip('()')
		cat = cat[1:-2]
		print('cat_from_Ratings =',cat)
		cat_header = cat.replace(',','')
		print('cat_header =', cat_header)

		cur.execute('''SELECT adj_rating FROM Ratings WHERE person_id=? AND cat_name=?''', (person_id, cat,))
		scores = cur.fetchall()
		print('== scores:',scores)

		sum_score = 0
		count_score = 0
		average_score = -1
		for item in scores:
			try:
				sum_score = sum_score + item[0]
			except:
				continue
			count_score = count_score + 1
			if (count_score > 0):
				average_score = sum_score / count_score
		print("== Average score = ", average_score)

		sql_command = "UPDATE Averages SET '" + cat_header + "'=" + str(average_score) + " WHERE person_id=" + person_id
		print(sql_command)
		cur.execute(sql_command)
		conn.commit()



conn.commit()
print('nice')
