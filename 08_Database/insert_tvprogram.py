weekdays = ["Воскресенье", "Понедельник", "Вторник", "Среда",
"Четверг", "Пятница", "Суббота", "Воскресенье"]

import sqlite3 as db
c = db.connect(database="tvprogram")
cu = c.cursor()
cu.execute("""DELETE FROM wd;""")
cu.executemany('INSERT INTO wd VALUES (?, ?);', enumerate(weekdays))
c.commit()
c.close()