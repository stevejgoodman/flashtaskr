import os

# grab the folder where the script lives
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = 'flasktaskr.db'
USERNAME = 'admin'
PASSWORD = 'admin'
WTF_CSRF_ENABLED = True  # cross-site request forgery prevention
SECRET_KEY = 'my_precious'

# define the full path to the DB
DATABASE_PATH = os.path.join(basedir, DATABASE)

