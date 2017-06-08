import sqlite as db
c = db.connect(database="tvprogram")
cu = c.cursor()
cu.execute("""
SELECT tvdate, tvtime1, wd.wdname, tvchannel, prname, prgenre
FROM tv, wd
WHERE wd.weekday = tvweekday
ORDER BY tvdate, tvtime1;
""")
for rec in cu.fetchall():
	dt = rec[0] + rec[1]
	weekday = rec[2]
	channel = rec[3]
	name = rec[4]
	genre = rec[5]
	print ("%s, %02i.%02i.%04i %s %02i:%02i %s (%s)" % (weekday, dt.day, dt.month, dt.year, channel,
dt.hour, dt.minute, name, genre))