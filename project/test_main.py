import os
import unittest

from views import app, db
from _config import basedir
from models import User

from views import bcrypt


TEST_DB = 'test.db'

class MainTests(unittest.TestCase):
    # setup/teardown before/after each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                                os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # helper methods
    def login(self, name, password):
        return self.app.post('/',
                             data=dict(name=name, password=password),
                            follow_redirects=True)

    def test_404_error(self):
        response = self.app.get('/this-route-does-not-exist')
        self.assertEquals(response.status_code, 404)

    def test_500_error(self):
        bad_user = User(
            name='Jeremy',
            email='Jeremy@realpython.com',
            password='django'
        )
        db.session.add(bad_user)
        db.session.commit()
        response = self.login('Jeremy', 'django')
        self.assertEquals(response.status_code, 500)


    if __name__ == "__main__":
        unittest.main()