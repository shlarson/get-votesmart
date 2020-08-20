import urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET
import sqlite3
print('start:')

conn = sqlite3.connect('averaged_scores.sqlite')
cur = conn.cursor()

#get list of persons
cur.execute('''SELECT DISTINCT person_id FROM Ratings''')
list_persons = cur.fetchall()
#print(type(list_persons), list_persons)

#get list of SIGs ; skips the first because it's typed weird?
cur.execute('''SELECT sig_code FROM Direction''')
list_sigcode = cur.fetchall()[1:]
#print('list_sigcode:',type(list_sigcode), list_sigcode)

#go through individual peeps:
for peep in list_persons:
    person_id = peep[0]
    print('=====  person_id:', person_id, ' =====')
    #get distinct key_id for person_id:
    cur.execute('''SELECT id FROM Ratings WHERE person_id=?''', (person_id,))
    keys_for_peep = cur.fetchall()
    #print(len(keys_for_peep), 'keys for this peep:', keys_for_peep)

    #get ratings per key_id:
    for line in keys_for_peep:
        key = str(line[0])
        cur.execute('''SELECT rating FROM Ratings WHERE id=?''', (key,))
        key_rating = cur.fetchone()[0]

        #need to convert rating:
        cur.execute('''SELECT sig_code FROM Ratings WHERE id=?''', (key,))
        key_sig = cur.fetchone()[0]
        print(' = key:', key, ' sig_code:', key_sig, ' rating:', key_rating)
        cur.execute('''SELECT direction FROM Direction WHERE sig_code=?''', (key_sig,))
        try:
            direct = cur.fetchone()[0]
            print('direction:', direct)
        except:
            continue

        if direct == 1:
            print('no direction change')
            if type(key_rating) is str:
                print('direction:', direct, '| error: rating is a string:',key_rating)
                if len(key_rating) <= 4:
                    print('letter grade =',key_rating[0])
                    if key_rating[0] == 'A':
                        key_rating = 100
                    elif key_rating[0] == 'B':
                        key_rating = 80
                    elif key_rating[0] == 'C':
                        key_rating = 60
                    elif key_rating[0] == 'D':
                        key_rating = 40
                    elif key_rating[0] == 'E':
                        key_rating = 20
                    elif key_rating[0] == 'F':
                        key_rating = 0
                    else:
                        key_rating = input('enter new value int 0-100:')
                        key_rating = int(key_rating)
                elif 'Fence Sitter' in key_rating:
                    key_rating = 50
                else:
                    key_rating = input('enter new value int 0-100:')
                    key_rating = int(key_rating)

            if key_rating > 1:
                key_rating = key_rating/100

            print('adjusted rating:', key_rating)
            cur.execute('''UPDATE Ratings SET adj_rating=? WHERE id=?''',(key_rating, key,) )
            conn.commit()
        else:
            print('reverse direction')
            if type(key_rating) is str:
                print('direction:', direct, '| error: rating is a string:',key_rating)
                if len(key_rating) <= 4:
                    print('letter grade =',key_rating[0])
                    if key_rating[0] == 'A':
                        key_rating = 100
                    elif key_rating[0] == 'B':
                        key_rating = 80
                    elif key_rating[0] == 'C':
                        key_rating = 60
                    elif key_rating[0] == 'D':
                        key_rating = 40
                    elif key_rating[0] == 'E':
                        key_rating = 20
                    elif key_rating[0] == 'F':
                        key_rating = 0
                    else:
                        key_rating = input('enter new value int 0-100:')
                        key_rating = int(key_rating)
                elif 'Fence Sitter' in key_rating:
                    key_rating = 50
                else:
                    key_rating = input('enter new value int 0-100:')
                    key_rating = int(key_rating)

            if key_rating > 1:
                key_rating = key_rating/100

            key_rating = 1 - key_rating
            print('adjusted rating:', key_rating)
            cur.execute('''UPDATE Ratings SET adj_rating=? WHERE id=?''',(key_rating, key,) )
            conn.commit()

print('nice')
