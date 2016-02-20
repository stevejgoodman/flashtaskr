# import sqlite3
from _config import DATABASE

# with sqlite3.connect(DATABASE_PATH) as connection:
#     c = connection.cursor()
#     c.execute("""CREATE TABLE tasks(task_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT NOT NULL, due_date TEXT NOT NULL,
#                 priority INTEGER NOT NULL, status INTEGER NOT NULL)""")
#
#     # insert dummy data
#     c.execute("""INSERT INTO tasks (name, due_date, priority, status)
#                   VALUES('Finish this tutorial','03/25/2013', 10, 1)""")
#     c.execute("""INSERT INTO tasks (name, due_date, priority, status)
#                   VALUES('Finish real python course 2','03/25/2013', 10, 1)""")


from views import db
from models import Task
from datetime import date

db.create_all()

# insert dummy data
#db.session.add(Task("Finish this tutorial", date(2015, 3, 13), 10, 1))
#db.session.add(Task("Finish realpython", date(2015, 3, 13), 10, 1))

db.session.commit()
