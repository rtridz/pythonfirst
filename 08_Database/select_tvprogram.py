import sqlite3 as db
c = db.connect(database="tvprogram")
cu = c.cursor()
cu.execute("SELECT   weekday,   wdname   FROM   wd   ORDER   BY weekday;")
for i, n in cu.fetchall():
	print (i, n)