import sqlite3 as db
c = db.connect(database="tvprogram")
cu = c.cursor()
try:
	cu.execute("""
CREATE TABLE tv (
tvdate DATE,
tvweekday INTEGER,
tvchannel VARCHAR(30),
tvtime1 TIME,
tvtime2 TIME,
prname VARCHAR(150),
prgenre VARCHAR(40)
);
""")
except db.DatabaseError, x:
	print ("Ошибка")
c.commit()
try:
	cu.execute("""
CREATE TABLE wd (
weekday INTEGER,
wdname VARCHAR(11)
);
""")
except db.DatabaseError:
	print ("Ошибка")