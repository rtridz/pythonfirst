import sqlite3 as db
c = db.connect(database="tvprogram")
cu = c.cursor()
try:
	cu.execute("""DROP TABLE tv;""")
except db.DatabaseError:
	print ("Ошибка")
c.commit()
try:
	cu.execute("""DROP TABLE wd;""")
except db.DatabaseError:
	print ("Ошибка")
c.commit()
c.close()