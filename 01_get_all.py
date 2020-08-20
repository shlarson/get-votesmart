import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import sqlite3

conn = sqlite3.connect('sigs14_16_18.sqlite')
cur = conn.cursor()

#FIND SENATE ONLY

cur.executescript('''
DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS Sigs;
DROP TABLE IF EXISTS State;
DROP TABLE IF EXISTS Candidate;
DROP TABLE IF EXISTS Person;
DROP TABLE IF EXISTS Scores;
DROP TABLE IF EXISTS Chamber;
DROP TABLE IF EXISTS Party;

CREATE TABLE "Categories" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"code"	TEXT NOT NULL UNIQUE
);

CREATE TABLE "Sigs" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"code"	TEXT NOT NULL UNIQUE,
    "cat_id" TEXT NOT NULL
);


CREATE TABLE "State" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"name"	TEXT NOT NULL UNIQUE
);

CREATE TABLE "Scores" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    "person_id" TEXT,
    "state_id" TEXT,
    "chamber_id" TEXT,
    "party_id" TEXT,
    "sig_id" TEXT,
    "cat_id" TEXT,
    "timespan" TEXT,
    "rating" INTEGER
);

CREATE TABLE "Person" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    "candidateId" TEXT UNIQUE,
    "firstname" TEXT,
    "lastname" TEXT
);

CREATE TABLE "Chamber" (
    "id"    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    "name" TEXT NOT NULL UNIQUE
);

CREATE TABLE "Party" (
    "id"   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    "name"  TEXT NOT NULL UNIQUE
);

''')


#no ID SIGs or Categories
sig_na=100000
cat_na=100000

#GET SENATE 2014
state_id='states_and_ids.txt'
s_i=open(state_id)
for line in s_i:
    words=line.split(' ')
    state=words[0].strip()
    print(state)

    cur.execute('''INSERT OR IGNORE INTO State (name)
        VALUES ( ? )''' , ( state , ) )
    cur.execute('SELECT id FROM State WHERE name = ? ', ( state, ) )
    state_id=cur.fetchone()[0]

    conn.commit()

### Plug in the API Key:
    serviceurl = 'https://api.votesmart.org/Candidates.getByOfficeTypeState?key=<APIKEY>&officeTypeId=C&stateId='+state+'&electionYear=2014'
    tree = ET.parse(urllib.request.urlopen(serviceurl))
    root = tree.getroot()
    print(serviceurl)

#tree start on candidate
    for child in root.findall('candidate'):
        #for winning candidates only in the Senate -> officeId=6
        elected = child.find('electionStatus').text
        officeId = child.find('electionOfficeId').text
        if elected == 'Won' and officeId == '6':
            print(elected)
            candidateId = child.find('candidateId').text
            firstName = child.find('firstName').text
            lastName = child.find('lastName').text
            chamber = child.find('officeName').text
            #partyId = child.find('electionParties').text
            print(elected, candidateId,':', firstName, lastName, ':', chamber)

            cur.execute('''INSERT OR IGNORE INTO Chamber ( name )
                VALUES ( ? )''' , ( chamber , ) )
            cur.execute('SELECT id FROM Chamber WHERE name = ? ', ( chamber, ) )
            try:
                chamber_id=cur.fetchone()[0]
            except: continue

            #cur.execute('''INSERT OR IGNORE INTO Candidate (candidateId, firstname, lastname , state_id, chamber_id )
            #    VALUES ( ?,?,?,?,? )''' , ( candidateId , firstName , lastName , state , chamber_id ) )
            #cur.execute('SELECT id FROM Candidate WHERE firstname = ? ', ( firstName, ) )
            #candidate_id=cur.fetchone()[0]

            conn.commit()

            #get detailed bio info (religion and PID)
            bio_url = 'https://api.votesmart.org/CandidateBio.getBio?key=<APIKEY>&candidateId='+candidateId
            tree2 = ET.parse(urllib.request.urlopen(bio_url))
            root2 = tree2.getroot()

            for child2 in root2.findall('candidate'):
                religion = child2.find('religion').text
                for child2 in root2.findall('office'):
                    partyId = child2.find('parties').text
                    print('religion:',religion, ', PID:', partyId)

                    cur.execute('''INSERT OR IGNORE INTO Party (name)
                        VALUES ( ? )''' , ( partyId , ) )
                    cur.execute('SELECT id FROM Party WHERE name = ? ', ( partyId, ) )
                    try:
                        party_id=cur.fetchone()[0]
                    except: party_id='NA'
                    conn.commit()

                #get rating from all SIGs
                rating_url = 'https://api.votesmart.org/Rating.getCandidateRating?key=<APIKEY>&candidateId='+candidateId
                tree3 = ET.parse(urllib.request.urlopen(rating_url))
                root3 = tree3.getroot()
                for child3 in root3.findall('rating'):
                    sigId = child3.find('sigId').text
                    #ratingId = child3.find('ratingId').text
                    ratingText = child3.find('ratingText').text
                    timespan = child3.find('timespan').text
                    score = child3.find('rating').text
                    categoryId = child3[2][0][0].text
                    #categoryName goes into a different thing
                    categoryName = child3[2][0][1].text
                    print(sigId, '=', score,'%', timespan, '<',categoryId,'>', categoryName)

                    #added the +1 counter Monday 11/25
                    #cur.execute('SELECT id FROM Sigs WHERE code = ? ', ( sigId, ) )
                    #try:
                    #    sig_id=cur.fetchone()[0]
                    #except:
                    #    sig_id = sig_na+1
                    #    sig_na = sig_na+1
                    cur.execute('''INSERT OR IGNORE INTO Categories ( name, code )
                        VALUES ( ?,? )''', ( categoryName, categoryId, ) )
                    cur.execute('SELECT id FROM Categories WHERE name = ?', (categoryName, ))
                    cat_id=cur.fetchone()[0]

                    #cur.execute('SELECT id FROM Categories WHERE code = ? ', ( categoryId, ) )
                    #try:
                    #    cat_id=cur.fetchone()[0]
                    #except:
                    #    cat_id = cat_na+1
                    #    cat_na = cat_na+1
                    cur.execute('''INSERT OR IGNORE INTO Sigs ( name, code, cat_id )
                        VALUES ( ?,?,? )''', ( ratingText, sigId, categoryId, ) )
                    cur.execute('SELECT id FROM Sigs WHERE code = ?', (sigId, ))
                    try:
                        sig_id=cur.fetchone()[0]
                    except:
                        sig_id=sig_na+1
                        sig_na=sig_na+1

					###

                    cur.execute('''INSERT OR IGNORE INTO Person ( candidateId, firstname, lastname)
                        VALUES ( ?,?,? )''', ( candidateId, firstName, lastName, ) )
                    cur.execute('SELECT id FROM Person WHERE candidateId = ?', (candidateId, ))
                    person_id=cur.fetchone()[0]

                    cur.execute('''INSERT OR IGNORE INTO Scores ( person_id, state_id, chamber_id , party_id , sig_id , cat_id , timespan , rating)
                        VALUES ( ?,?,?,?,?,?,?,? )''' , ( person_id , state_id , chamber_id , party_id , sig_id , cat_id , timespan , score ) )
                    cur.execute('SELECT id FROM Scores WHERE rating = ? ', ( score, ) )

                    conn.commit()


#GET SENATE 2016
state_id='states_and_ids.txt'
s_i=open(state_id)
for line in s_i:
    words=line.split(' ')
    state=words[0].strip()
    print(state)

    cur.execute('''INSERT OR IGNORE INTO State (name)
        VALUES ( ? )''' , ( state , ) )
    cur.execute('SELECT id FROM State WHERE name = ? ', ( state, ) )
    state_id=cur.fetchone()[0]

    conn.commit()

    serviceurl = 'https://api.votesmart.org/Candidates.getByOfficeTypeState?key=<APIKEY>&officeTypeId=C&stateId='+state+'&electionYear=2016'
    tree = ET.parse(urllib.request.urlopen(serviceurl))
    root = tree.getroot()
    print(serviceurl)

#tree start on candidate
    for child in root.findall('candidate'):
        #for winning candidates only in the Senate -> officeId=6
        elected = child.find('electionStatus').text
        officeId = child.find('electionOfficeId').text
        if elected == 'Won' and officeId == '6':
            print(elected)
            candidateId = child.find('candidateId').text
            firstName = child.find('firstName').text
            lastName = child.find('lastName').text
            chamber = child.find('officeName').text
            #partyId = child.find('electionParties').text
            print(elected, candidateId,':', firstName, lastName, ':', chamber)

            cur.execute('''INSERT OR IGNORE INTO Chamber ( name )
                VALUES ( ? )''' , ( chamber , ) )
            cur.execute('SELECT id FROM Chamber WHERE name = ? ', ( chamber, ) )
            try:
                chamber_id=cur.fetchone()[0]
            except: continue

            #cur.execute('''INSERT OR IGNORE INTO Candidate (candidateId, firstname, lastname , state_id, chamber_id )
            #    VALUES ( ?,?,?,?,? )''' , ( candidateId , firstName , lastName , state , chamber_id ) )
            #cur.execute('SELECT id FROM Candidate WHERE firstname = ? ', ( firstName, ) )
            #candidate_id=cur.fetchone()[0]

            conn.commit()

            #get detailed bio info (religion and PID)
            bio_url = 'https://api.votesmart.org/CandidateBio.getBio?key=<APIKEY>&candidateId='+candidateId
            tree2 = ET.parse(urllib.request.urlopen(bio_url))
            root2 = tree2.getroot()

            for child2 in root2.findall('candidate'):
                religion = child2.find('religion').text
                for child2 in root2.findall('office'):
                    partyId = child2.find('parties').text
                    print('religion:',religion, ', PID:', partyId)

                    cur.execute('''INSERT OR IGNORE INTO Party (name)
                        VALUES ( ? )''' , ( partyId , ) )
                    cur.execute('SELECT id FROM Party WHERE name = ? ', ( partyId, ) )
                    try:
                        party_id=cur.fetchone()[0]
                    except: party_id='NA'
                    conn.commit()

                #get rating from all SIGs
                rating_url = 'https://api.votesmart.org/Rating.getCandidateRating?key=<APIKEY>&candidateId='+candidateId
                tree3 = ET.parse(urllib.request.urlopen(rating_url))
                root3 = tree3.getroot()
                for child3 in root3.findall('rating'):
                    sigId = child3.find('sigId').text
                    #ratingId = child3.find('ratingId').text
                    ratingText = child3.find('ratingText').text
                    timespan = child3.find('timespan').text
                    score = child3.find('rating').text
                    categoryId = child3[2][0][0].text
                    #categoryName goes into a different thing
                    categoryName = child3[2][0][1].text
                    print(sigId, '=', score,'%', timespan, '<',categoryId,'>', categoryName)

                    #added the +1 counter Monday 11/25
                    #cur.execute('SELECT id FROM Sigs WHERE code = ? ', ( sigId, ) )
                    #try:
                    #    sig_id=cur.fetchone()[0]
                    #except:
                    #    sig_id = sig_na+1
                    #    sig_na = sig_na+1
                    cur.execute('''INSERT OR IGNORE INTO Categories ( name, code )
                        VALUES ( ?,? )''', ( categoryName, categoryId, ) )
                    cur.execute('SELECT id FROM Categories WHERE name = ?', (categoryName, ))
                    cat_id=cur.fetchone()[0]

                    #cur.execute('SELECT id FROM Categories WHERE code = ? ', ( categoryId, ) )
                    #try:
                    #    cat_id=cur.fetchone()[0]
                    #except:
                    #    cat_id = cat_na+1
                    #    cat_na = cat_na+1
                    cur.execute('''INSERT OR IGNORE INTO Sigs ( name, code, cat_id )
                        VALUES ( ?,?,? )''', ( ratingText, sigId, categoryId, ) )
                    cur.execute('SELECT id FROM Sigs WHERE code = ?', (sigId, ))
                    try:
                        sig_id=cur.fetchone()[0]
                    except:
                        sig_id=sig_na+1
                        sig_na=sig_na+1

					###

                    cur.execute('''INSERT OR IGNORE INTO Person ( candidateId, firstname, lastname)
                        VALUES ( ?,?,? )''', ( candidateId, firstName, lastName, ) )
                    cur.execute('SELECT id FROM Person WHERE candidateId = ?', (candidateId, ))
                    person_id=cur.fetchone()[0]

                    cur.execute('''INSERT OR IGNORE INTO Scores ( person_id, state_id, chamber_id , party_id , sig_id , cat_id , timespan , rating)
                        VALUES ( ?,?,?,?,?,?,?,? )''' , ( person_id , state_id , chamber_id , party_id , sig_id , cat_id , timespan , score ) )
                    cur.execute('SELECT id FROM Scores WHERE rating = ? ', ( score, ) )

                    conn.commit()

#GET ALL 2018
state_id='states_and_ids.txt'
s_i=open(state_id)
for line in s_i:
    words=line.split(' ')
    state=words[0].strip()
    print(state)

    cur.execute('''INSERT OR IGNORE INTO State (name)
        VALUES ( ? )''' , ( state , ) )
    cur.execute('SELECT id FROM State WHERE name = ? ', ( state, ) )
    state_id=cur.fetchone()[0]

    conn.commit()

    serviceurl = 'https://api.votesmart.org/Candidates.getByOfficeTypeState?key=<APIKEY>&officeTypeId=C&stateId='+state+'&electionYear=2018'
    tree = ET.parse(urllib.request.urlopen(serviceurl))
    root = tree.getroot()
    print(serviceurl)

#tree start on candidate
    for child in root.findall('candidate'):
        #for winning candidates only in the Senate -> officeId=6,5
        elected = child.find('electionStatus').text
        if elected == 'Won':
            print(elected)
            candidateId = child.find('candidateId').text
            firstName = child.find('firstName').text
            lastName = child.find('lastName').text
            chamber = child.find('officeName').text
            #partyId = child.find('electionParties').text
            print(elected, candidateId,':', firstName, lastName, ':', chamber)

            cur.execute('''INSERT OR IGNORE INTO Chamber ( name )
                VALUES ( ? )''' , ( chamber , ) )
            cur.execute('SELECT id FROM Chamber WHERE name = ? ', ( chamber, ) )
            try:
                chamber_id=cur.fetchone()[0]
            except: continue

            #cur.execute('''INSERT OR IGNORE INTO Candidate (candidateId, firstname, lastname , state_id, chamber_id )
            #    VALUES ( ?,?,?,?,? )''' , ( candidateId , firstName , lastName , state , chamber_id ) )
            #cur.execute('SELECT id FROM Candidate WHERE firstname = ? ', ( firstName, ) )
            #candidate_id=cur.fetchone()[0]

            conn.commit()

            #get detailed bio info (religion and PID)
            bio_url = 'https://api.votesmart.org/CandidateBio.getBio?key=<APIKEY>&candidateId='+candidateId
            tree2 = ET.parse(urllib.request.urlopen(bio_url))
            root2 = tree2.getroot()

            for child2 in root2.findall('candidate'):
                religion = child2.find('religion').text
                for child2 in root2.findall('office'):
                    partyId = child2.find('parties').text
                    print('religion:',religion, ', PID:', partyId)

                    cur.execute('''INSERT OR IGNORE INTO Party (name)
                        VALUES ( ? )''' , ( partyId , ) )
                    cur.execute('SELECT id FROM Party WHERE name = ? ', ( partyId, ) )
                    try:
                        party_id=cur.fetchone()[0]
                    except: party_id='NA'
                    conn.commit()

                #get rating from all SIGs
                rating_url = 'https://api.votesmart.org/Rating.getCandidateRating?key=<APIKEY>&candidateId='+candidateId
                tree3 = ET.parse(urllib.request.urlopen(rating_url))
                root3 = tree3.getroot()
                for child3 in root3.findall('rating'):
                    sigId = child3.find('sigId').text
                    #ratingId = child3.find('ratingId').text
                    ratingText = child3.find('ratingText').text
                    timespan = child3.find('timespan').text
                    score = child3.find('rating').text
                    categoryId = child3[2][0][0].text
                    #categoryName goes into a different thing
                    categoryName = child3[2][0][1].text
                    print(sigId, '=', score,'%', timespan, '<',categoryId,'>', categoryName)

                    #added the +1 counter Monday 11/25
                    #cur.execute('SELECT id FROM Sigs WHERE code = ? ', ( sigId, ) )
                    #try:
                    #    sig_id=cur.fetchone()[0]
                    #except:
                    #    sig_id = sig_na+1
                    #    sig_na = sig_na+1
                    cur.execute('''INSERT OR IGNORE INTO Categories ( name, code )
                        VALUES ( ?,? )''', ( categoryName, categoryId, ) )
                    cur.execute('SELECT id FROM Categories WHERE name = ?', (categoryName, ))
                    cat_id=cur.fetchone()[0]

                    #cur.execute('SELECT id FROM Categories WHERE code = ? ', ( categoryId, ) )
                    #try:
                    #    cat_id=cur.fetchone()[0]
                    #except:
                    #    cat_id = cat_na+1
                    #    cat_na = cat_na+1
                    cur.execute('''INSERT OR IGNORE INTO Sigs ( name, code, cat_id )
                        VALUES ( ?,?,? )''', ( ratingText, sigId, categoryId, ) )
                    cur.execute('SELECT id FROM Sigs WHERE code = ?', (sigId, ))
                    try:
                        sig_id=cur.fetchone()[0]
                    except:
                        sig_id=sig_na+1
                        sig_na=sig_na+1

					###

                    cur.execute('''INSERT OR IGNORE INTO Person ( candidateId, firstname, lastname)
                        VALUES ( ?,?,? )''', ( candidateId, firstName, lastName, ) )
                    cur.execute('SELECT id FROM Person WHERE candidateId = ?', (candidateId, ))
                    person_id=cur.fetchone()[0]

                    cur.execute('''INSERT OR IGNORE INTO Scores ( person_id, state_id, chamber_id , party_id , sig_id , cat_id , timespan , rating)
                        VALUES ( ?,?,?,?,?,?,?,? )''' , ( person_id , state_id , chamber_id , party_id , sig_id , cat_id , timespan , score ) )
                    cur.execute('SELECT id FROM Scores WHERE rating = ? ', ( score, ) )

                    conn.commit()
