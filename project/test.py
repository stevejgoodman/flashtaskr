import os
import unittest

from views import app, db
from _config import basedir
from models import User

TEST_DB = 'test.db'


class AllTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +\
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_setup(self):
        new_user = User('stevejg', 'stevejg@hotmail.com', 'stevejg')
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        for t in test:
            t.name
        assert (t.name =='stevejg')

    def test_form_is_present_on_login_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please sign in to access your task list', response.data)

    def login(self, name, password):
        return self.app.post('/', data=dict(name=name, password=password),
                             follow_redirects=True)

    def test_users_cannot_login_unless_registered(self):
        response = self.login('food', 'bar')
        self.assertIn('Invalid login credentials', response.data)

    def register(self, name, email, password, confirm):
        return self.app.post(
            'register/',
            data=dict(name=name, email=email, password=password, confirm=confirm),
            follow_redirects=True
        )

    # Hmmm not sure about this - surely form validation should fail on password?
    def test_users_can_login(self):
        self.register('newstevejg', 'newstevejg', 'steve', 'stevejg')
        response = self.login('newstevejg', 'newstevejg')
        self.assertIn('Welcome', response.data)

    # def test_invalid_form_date(self):
    #     self.register('newstevejg', 'newstevejg', 'steve', 'stevejg')
    #     response = self.login('alert("alert box!");', 'foo')
    #     self.assertIn(b'Invalid username or password', response.data)

    def test_form_is_present_on_register_page(self):
        response = self.app.get('register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please register', response.data)

    def test_user_registration(self):
        self.app.get('register/', follow_redirects=True)
        response = self.register('michael', 'michael@realpython.com', 'python', 'python')
        self.assertIn(b'thanks for registering', response.data)

    # test duplicate users
    def test_user_registration_error(self):
        self.app.get('register/', follow_redirects=True)
        response = self.register('michael', 'michael@realpython.com', 'python', 'python')
        self.app.get('register/', follow_redirects=True)
        response = self.register('michael', 'michael@realpython.com', 'python', 'python')
        self.assertIn(b'User already exists with that name', response.data)

    def logout(self):
        return self.app.get('logout/', follow_redirects=True)

    def test_logged_in_users_can_logout(self):
        # self.register('michael', 'michael@realpython.com', 'python', 'python')
        self.login('michael', 'python')
        response = self.logout()
        self.assertIn(b'Welcome', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        #dont want to find goodbye this time because shouldnt be able to see logged out screen
        self.assertNotIn(b'Goodbye', response.data)

    def create_user(self, name, email, password):
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

    def create_task(self):
        return self.app.post('add/', data=dict(
            name='Go to the bank',
            due_date='02/05/2015',
            priority='1',
            posted_date='02/04/2014',
            status='1'
         ), follow_redirects=True)

    def test_users_can_add_tasks(self):
        self.create_user('michael', 'michael@realpython','python')
        self.login('michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'New entry successfully posted', response.data)

    def test_users_can_complete_tasks(self):
        self.create_user('michael', 'michael@realpython','python')
        self.login('michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertIn(b'task was marked as complete', response.data)

    def test_users_can_delete_tasks(self):
        self.create_user('michael', 'michael@realpython','python')
        self.login('michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertIn(b'task was deleted', response.data)

if __name__ == '__main__':
    unittest.main()
